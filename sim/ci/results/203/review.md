# PR 203 review draft: authentic 49-byte DualShock 3 input report

Verdict: DEMONSTRATED (tested as the PR merged onto current main; the PR as submitted is 379 commits behind main)

## What was tested and how
Remapper A (usb2usb, PS3 as the default USB output mode) in Simantic's RP2040 simulator (pyrite, local unreleased build), with the device-side HID IN reports captured by --usb-hid-tap usb. Inputs are fed over the uart_peer link (Cross, left stick up-right, right stick down-left, Cross+L2 full), 8 ms per tick. Three builds: main (9fa79f45), the PR branch as submitted (c03f2bc8) and a local merge of the PR onto main (203m; only ps3_descriptors.h differs from main). Script: scenarios/203.sh; logs results/203/review/ps3.{main,203,203m}.*. The PR as submitted is not a clean comparison to main (the L2 digital bit differs because of unrelated older code), so the 203m comparison is the one that isolates the change. The reference layout is Linux drivers/hid/hid-sony.c: sixaxis_raw_event() ignores any report whose size is not 49 or whose first byte is not 0x01, reads the battery byte at offset 30 and the accelerometers at SIXAXIS_INPUT_REPORT_ACC_X_OFFSET = 41 (bytes 41..48, big-endian on the wire).

## Results
| | main | PR merged on main (203m) |
|---|---|---|
| report length | 50 | 49 |
| accelerometer/gyro bytes | start at 42 (one extra 00 at 41): 00 02 00 02 00 02 00 02 00 | start at 41: 02 00 02 00 02 00 02 00 |
| descriptor Input size (parsed from the header) | 49 data bytes + ID = 50 | 48 + ID = 49 |
| bytes 0..40 | identical to 203m for all 271 reports | |
| battery (offset 30) / connection (31) | 05 / 10 | 05 / 10 |
Same buttons, sticks and L2 pressure in every distinct report (Cross 00 40 00, left stick 255/0, right stick 0/255, L2 00 41 00 with pressure 255).

Hence with 49 bytes the report passes hid-sony.c's size check and the motion data lands at offset 41; on main the 50-byte report would be dropped by that check, and a console reading fixed offsets would see motion one byte late, as the PR states.

## Bugs or regressions
None in the merged result. The report-descriptor edits are collection type labels plus Report Count 40 -> 39; I did not enumerate the descriptor with a host parser.

## Not covered
A real PS3 or Linux host (I compared the bytes to the hid-sony.c source, I did not run the driver); motion values other than the constant 0x0200; Bluetooth/other output modes; the feature reports (0xEE, 0xEF, 0xF2) and the GET_REPORT path; physical hardware.
