# PR 292: fix(nuon): light the KB2040 NeoPixel on usb2nuon via PIO1 (#257)
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 9 s, nRF 14 s, total 62 s
What the PR changes: `src/CMakeLists.txt` switches the `joypad_nuon` (usb2nuon_kb2040) target from CONFIG_NO_NEOPIXEL=1 to CONFIG_NEOPIXEL_USE_PIO1=1 (2 lines).
Covered by this test: no. The change applies only to the usb2nuon_kb2040 target. The harness builds usb2usb_remapper_v7_a and bt2usb, and neither uses that flag.
Evidence: `results/292/summary.json` result "pass", touched_files rp2040: src/CMakeLists.txt; the RP2040 build is joypad_usb2usb_remapper_v7_a only.
