# PR 277 adversarial: BT discovery policy (BT.DISCOVERY.SET, AUTO/BONDED/OFF)

Binary: sim-main, nRF bt2usb (`scn/elf/nrf_main.elf` vs `nrf_277.elf`), scripted BLE pad (`nrf_ble.yaml`), CDC host (`scn/sim/cdc_host.py`). Script `scenarios/adv/277_adv.sh`; logs `results/277/adv/`. BLE only: Classic inquiry is not simulable.

| # | Attack | main | PR 277 |
|---|---|---|---|
| 1-5 | `BT.DISCOVERY.SET mode=2` (OFF) sent at 1.09, 1.15, 1.44, 1.45, 1.82 s, i.e. while the pad is being connected (connect 1.046 s, link 1.178 s) and paired (1.575 s); `mode=0` at 4 s | command unknown; pad connects and pairs | pad connects and pairs every time, `connections:1`, discovery returns to 0 |
| 6 | mode -1, 3, 4294967297, "1" (string), missing | unknown command | `Invalid mode` for all five; discovery stays 0 |
| 7 | mode 1.9 | unknown command | accepted as 1 (BONDED): `json_get_int` truncates (pre-existing helper) |
| 8 | several BLE pads / a stranger pad while one is bonded | not run | not run: every scripted BLE peer advertises the same fixed address C1:23:45:67:89:AB, so a second device cannot be told from the first (simulator gap) |

## Findings
No PR-INTRODUCED defect shown (attacks 1-7 NONE).
**PR-INCOMPLETE (by reading, not simulated): BONDED does nothing for BLE.** In `btstack_host.h` the PR says "BLE discovery is unaffected by the policy"; the only BLE-side change is that OFF stops the scan. The BLE advertising handler has no `discovery_mode` check, so with BONDED a stranger BLE pad that advertises the HID service is still connected, which is the "grabbing every controller in the room" the title describes. Suggested fix: in the BLE adv handler, when `discovery_mode == BT_DISCOVERY_BONDED` and the bond list is non-empty, skip addresses not in the LE device DB unless `scan_explicit_window`.
**Design risk (reading): OFF makes bonded BLE pads unreachable.** BLE pads never page the host, they only advertise; with the background scan off a bonded BLE pad cannot reconnect until `BT.SCAN`. The header comment promises "bonded controllers that page the host" works, which is only true for Classic.
Not run: OFF set while a connect attempt is failing (needs a BLE peer that stops answering; `btstack_host_stop_scan()` sets `BLE_STATE_IDLE` unconditionally and the connect timeout only fires in CONNECTING).
