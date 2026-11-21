# PR 226: feat(wiiext): add usb2wiiext — USB controllers into the Wii extension port
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 13 s / nRF 19 s; runs RP 56 s / nRF 13 s; behind_main 0
What the PR changes: new usb2wiiext app (app.c, app.h, app_config.h) for RP2040 kb2040 and Pi Pico, with Makefile and src/CMakeLists.txt targets that reuse wii_ext_device.c and wii_ext_crypto.c.
Covered by this test: no. The harness builds only usb2usb_remapper_v7_a and bt2usb, so the new usb2wiiext targets are never compiled, and the RP2040 and nRF scenarios do not run the app.
Evidence: summary.json checks 13/13, failing_vs_main []; build_rp_ok 1 is usb2usb_remapper_v7_a only; touched_files rp2040 (Makefile, src/CMakeLists.txt) and usb (app files).
