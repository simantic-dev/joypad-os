# PR 305: feat(switch_bt): pair over CDC and show a live console link on the LED
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 3 s, nRF 29 s, total 177 s
What the PR changes: adds a Switch (BT) branch to the CDC `BLE.PAIR` command (sync/re-pair), and makes the universal app LED solid while linked to a Switch; also `ble_output_is_connected()` returns the switch_bt link state in BT mode.
Covered by this test: no. `cdc_commands.c` is compiled into both the RP2040 usb2usb and the nRF bt2usb builds (object files present), but the new BLE.PAIR branch only runs when a host sends that CDC command, and no BLE.PAIR appears in either run's logs. `src/apps/universal/app.c` and `src/bt/ble_output/ble_output.c` are not in either build's object set (no ble_output object in the nRF or RP2040 build dirs), so neither scenario runs them.
Evidence: `results/305/summary.json` result "pass", failing_vs_main []; touched_files usb: cdc_commands.c, bt: ble_output.c; build dirs `build/lane-a/rp` and `build/lane-a/nrf` contain cdc_commands.c.o / cdc_commands.c.obj but no ble_output.c object.
