# PR 192: fix(bt): bind NSO retro pads (SNES/NES/N64/Genesis) to the Switch driver
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 10 s / nRF 20 s; runs RP 33 s / nRF 7 s; behind_main 0
What the PR changes: switch_pro_bt.c (classic BT Switch driver): adds a model enum selected by device name (SNES/NES/N64/MD), per-model button decode, and name-based switch_match() for the NSO pads.
Covered by this test: no. The driver is compiled into the nRF build and registers at boot ("[BTHID] Registered driver: Switch Pro" in nrf_ble.console.txt), but switch_match() runs only for classic BT discovery. The scripted pad is a BLE HOGP device, and the RP2040 run has no Bluetooth. No NSO pad is run.
Evidence: summary.json checks 13/13, failing_vs_main []; touched_files bt and usb (switch_pro_bt.c); nrf_ble.console.txt registration line only.
