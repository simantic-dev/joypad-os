# PR 290 adversarial: Xbox BLE rumble retry when a write is in flight

Binary: sim-main (BLE adv_data, SMP). nRF bt2usb ELFs `scn/elf/nrf_main.elf` / `nrf_290.elf`, scripted Xbox BLE pad (`scn/sim/peers/ble_xbox.py`, write response held HOLD x 50 ms), USB host sends SInput haptic START then STOP 20 ms later (`scn/sim/xbox_rumble_adv.py`). Script `scenarios/adv/290_adv.sh`; logs `results/290/adv/<case>.<main|290>.{pad,host,console}.txt` (`pad.txt` = writes the pad received).

| case | main | PR 290 |
|---|---|---|
| h3pair (response 150 ms) | START only, `status=0x0C`, STOP lost | START then STOP (fix works) |
| h16pair (response 800 ms) | START only, `status=0x0C` | **START only, STOP never sent, no log line** |
| h40pair (response 2 s) | START only | **START only, STOP never sent** |
| h3flood (10 x START/STOP, 20 ms apart, response 150 ms) | 3 START + 1 STOP reach the pad, last = STOP, 16 `status=0x0C` errors | START,STOP,START,STOP, last = STOP |

## Findings
**PR-INCOMPLETE (medium): the retry gives up after 500 ms and marks the lost STOP as sent.** `RUMBLE_RETRY_TIMEOUT_MS 500`: when the write response takes longer than that (long connection interval, slave latency, a busy pad), the `if (!bthid_send_output_report(...))` block falls through to `gp->rumble_retrying = false; gp->rumble_left = left; ...; feedback_clear_dirty()`, so the dropped STOP is considered delivered and never resent. The motor keeps running for the 0xFF "continuous" duration, exactly the bug the PR sets out to fix; the `BLE send_write_report failed` line is also gone (COMMAND_DISALLOWED is now silent), so nothing in the log shows it. Repro: `h16pair.290.pad.txt` (one write only) and `h40pair.290.pad.txt`. Fix: never give up on a stop (`left==0 && right==0`) while the link is up; or retry on the write-complete event instead of a wall-clock budget; at least keep `rumble_dirty` and the old `rumble_left/right` when the timeout expires.
Not shown: the PR's static-buffer copy overwrites `ble_report_buf[ble_index]` before knowing whether `hids_client_send_write_report` accepts the write. BTstack keeps the pointer until the ATT PDU is built (`W2_SEND_WRITE_REPORT` -> `gatt_client_write_value_of_characteristic`), so a rejected second send can change the bytes of an accepted-but-not-yet-sent first one. The sim did not hit the window (the PDU is built within the same run-loop pass); different report ids/lengths on one connection would make it visible. Reading, not demonstrated.
