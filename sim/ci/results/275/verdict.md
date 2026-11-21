# PR 275: fix(usb/ds4): normalize touchpad coordinates; add Nacon Revolution Pro Controller 2
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 1 s / nRF 17 s; runs RP 46 s / nRF 11 s; behind_main 0
What the PR changes: USB host DS4 driver: touch coordinates normalized with touch_norm_from_range (was raw 1919x942), an IMU calibration feature-report request at mount (hid.c and ds4_request_calibration), the 146b:0d02 PID added to is_sony_ds4(), plus docs.
Covered by this test: no. All three changed files are USB host code (sony_ds4.c, sony_ds4.h, hid.c). The RP2040 run has no USB HID controller on the remapper's host port (see PR 286), and the nRF run's pad is BLE HOGP, so none of the DS4 touch, calibration request or PID match executes.
Evidence: summary.json checks 13/13, failing_vs_main []; touched_files usb only; refresh.peer.txt "usb device 2b81:0101" is the remapper's own device.
