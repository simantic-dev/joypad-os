# PR 290: fix(bt): retry Xbox rumble when a BLE write is still in flight
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 2 s, nRF 39 s, total 150 s
What the PR changes: `bthid_gamepad.c` keeps the rumble state dirty and retries when `bthid_send_output_report()` is rejected (500 ms cap); `btstack_host.c` copies the report into a static buffer and treats COMMAND_DISALLOWED as non-error.
Covered by this test: partly. Both files are compiled into the nRF bt2usb build and the BLE HOGP pad path runs in the scenario (pairing, A, B+START, stick), but the rumble retry branch is reached only when the host requests rumble. The scenario sends no rumble (no rumble lines in the nRF or RP2040 logs), so the changed branches do not run. Not covered: the Xbox rumble issue itself.
Evidence: `results/290/summary.json` result "pass", touched_files bt: bthid_gamepad.c, btstack_host.c (both present as objects in the nRF build dir); no rumble in `results/main` logs.
