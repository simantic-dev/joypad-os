# PR 275 adversarial: DS4 touch normalisation, Nacon 146b:0d02, calibration GET_REPORT 0x02

Binary: sim-main (origin/main 4b5b5aee8), native USB host, remapper B built from main (9fa79f45) and ci-pr-275. Script `scenarios/adv/275_adv.sh`, peer options in `scenarios/peers/usb_ds4.py` (`OPT`). Logs `results/275/adv/<opt>.<main|275>.*`.

| # | Attack | main | PR 275 |
|---|---|---|---|
| 1 | baseline DS4 | no GET_REPORT, touch raw | GET_REPORT 0x02 sent once, mount continues, Player 1 assigned |
| 2 | touch values past the pad range: fingers at 12-bit 4094 and 2047/1023 (pad is 1919x942) | raw 4094 / 2047 forwarded | clamped: 65535 and 32784/16392; no wrap |
| 3 | 0x02 reply 64 B for a 37 B request | n/a (never asked) | accepted, truncated by TinyUSB, no fault, input continues |
| 4 | 0x02 reply 3 B (short) | n/a | no fault, input continues |
| 5 | 0x02 reply 0 B | n/a | no fault, input continues |
| 6 | 0x02 STALL | n/a | no fault, input continues |
Not run: reply NAK forever (ScriptedUsbDevice cannot NAK a control data stage, see SUMMARY simulator gaps); replug during the GET_REPORT (no run-time unplug for the RP2040 native host).

Static check: `touch_norm_from_range` clamps below 0 and above max, so any 12-bit device value is safe. `report_id == 0x02` is consumed before the DS4 auth state machine; DS4 auth uses 0xF0-0xF3, so no collision.

## Findings
None. Classification: NONE for all six attacks.
