# PR 291: feat(ps3): square stick range in PS3 mode (#143)
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 10 s, nRF 15 s, total 85 s
What the PR changes: `ps3_mode.c` scales each stick by radius / max(|x|,|y|) in the PS3 report path (on by default via PS3_SQUARE_STICKS), skipped for has_pressure sources.
Covered by this test: no. `ps3_mode.c` is compiled into the RP2040 usb2usb build, but that image runs in PS5 output mode, so `ps3_mode_send_report()` is never called. The nRF bt2usb scenario does not use the USB PS3 mode.
Evidence: `results/291/summary.json` result "pass", touched_files usb: src/usb/usbd/modes/ps3_mode.c; ps5default.cmake sets USB_OUTPUT_MODE_PS5.
