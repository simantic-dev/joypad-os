# PR 282: Add Pro Micro nRF52840 (nice!nano / SuperMini) board target
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 0 s (cached) / nRF 15 s; runs RP 80 s / nRF 14 s; behind_main 0
What the PR changes: new promicro_nrf52840 board (overlay, conf, pm yml), Pro Micro branches in button_nrf.c, ws2812_nrf.c (single active-high LED on P0.15) and main.c, a set_rgb() polarity change under the LED_SINGLE_PIN guard, seesaw_begin() retry for the JoyWing, and a bt2usb banner.
Covered by this test: partly. The Feather bt2usb build and boot run the shared nRF files and the BTstack central, so the common build and boot compile and run. The Pro Micro board target, its pin/LED code, the set_rgb() polarity change (no LED_SINGLE_PIN on the Feather) and seesaw_begin() (universal app only) are not run by either scenario. Result is not_exercised because the PR's new code is outside the run.
Evidence: summary.json checks 13/13, failing_vs_main []; touched_files nrf/* and bt2usb app.c; build_nrf_ok 1 for the Feather target only.
