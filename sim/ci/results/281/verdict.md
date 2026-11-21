# PR 281: feat(nrf): nice!nano / nRF52840 Pro Micro / SuperMini build target
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 1 s (cached) / nRF 21 s; runs RP 40 s / nRF 10 s; behind_main 0
What the PR changes: nice_nano build for the nRF52840 Pro Micro (promicro_nrf52840 board, uf2 pm yml), BOARD_NICE_NANO branches in bt2usb app.c, main.c (status LED P0.15) and button_nrf.c, DISABLE_USER_BUTTON for promicro in nrf/CMakeLists.txt, CI targets, docs.
Covered by this test: no. The harness builds only the Feather bt2usb; the nice_nano branches are compiled out there and the nice_nano board is never built or booted. The PR body says it is untested on hardware.
Evidence: summary.json checks 13/13, failing_vs_main []; build_nrf_ok 1 is the Feather target; the BOARD_NICE_NANO #elif blocks are not selected for it.
