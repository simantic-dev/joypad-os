# PR 296: feat(usb/switch): SELECT+START triggers Capture in Switch mode
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 2 s, nRF 26 s, total 98 s
What the PR changes: in `switch_mode_send_report()`, holding SELECT+START replaces Minus/Plus with Capture (A2).
Covered by this test: no. `switch_mode.c` is compiled into the RP2040 usb2usb build, but the RP2040 image is built with `USBD_DEFAULT_MODE=PS5` (ps5default.cmake), so the Switch report path is never selected. The nRF bt2usb build does not use the USB device output modes in the scenario.
Evidence: `results/296/summary.json` result "pass", touched_files usb: src/usb/usbd/modes/switch_mode.c; ps5default.cmake sets USB_OUTPUT_MODE_PS5.
