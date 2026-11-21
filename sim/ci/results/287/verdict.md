# PR 287: fix(alpakka): don't run the button service on the touch sense pin
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 24 s, nRF 37 s, total 148 s
What the PR changes: `src/CMakeLists.txt` sets `USE_BOOTSEL_BUTTON=1` for the controller_alpakka target instead of `BUTTON_USER_GPIO` (1 line).
Covered by this test: no. The change applies only to the controller_alpakka target. The harness builds usb2usb_remapper_v7_a and bt2usb.
Evidence: `results/287/summary.json` result "pass", touched_files rp2040: src/CMakeLists.txt; RP2040 build is joypad_usb2usb_remapper_v7_a only.
