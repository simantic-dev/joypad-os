# PR 286: fix(switch2): don't let a failed bulk transfer or long descriptor kill USB init
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 18 s / nRF 25 s; runs RP 43 s / nRF 13 s; behind_main 0
What the PR changes: Switch 2 Pro USB host driver (switch2_pro.c): a failed bulk transfer now clears xfer_pending and retries each init command up to 3 times, and a config descriptor longer than the buffer is walked truncated instead of rejected.
Covered by this test: no. The file is compiled into the RP2040 usb2usb remapper build, but the RP run never runs a USB host driver: peer.py is the USB host that enumerates the remapper's own device side (usb device 2b81:0101 in refresh.peer.txt), and the gamepad input comes over UART. No Switch 2 Pro (057e) is attached to the remapper's host port, and the nRF run has no USB host input either.
Evidence: refresh.peer.txt "usb device 2b81:0101"; nrf_ble.txt "usb device 2e8a:10c6"; summary.json checks 13/13, failing_vs_main []; touched_files usb only (switch2_pro.c).
