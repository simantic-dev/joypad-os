# PR 285: fix(ds5): match the DualSense Edge on USB host
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 0 s (cached) / nRF 14 s; runs RP 32 s / nRF 8 s; behind_main 0
What the PR changes: adds USB PID 054c:0df2 (DualSense Edge) to is_sony_ds5() in the USB host DS5 driver, so the Edge gets the DS5 driver instead of the generic HID parser.
Covered by this test: no. is_sony_ds5() is in the USB host path, which the RP2040 run does not exercise (no USB HID controller on the remapper's host port; see PR 286). The nRF run's Sony DualSense driver is the classic BTHID one, and the scripted pad is a BLE HOGP pad, so the changed match never runs.
Evidence: summary.json checks 13/13, failing_vs_main []; refresh.peer.txt "usb device 2b81:0101" is the remapper's own device, not a host-side controller; nrf_ble.console.txt "[BTHID] Registered driver: Sony DualSense" is registration only.
