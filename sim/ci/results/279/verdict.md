# PR 279: fix(bt): don't touch BTstack bonds before BT is started (usb2gc config-mode crash, #278)
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 1 s (cached) / nRF 18 s; runs RP 40 s / nRF 9 s; behind_main 0
What the PR changes: btstack_host_list_classic_bonds() returns 0 until hid_state.initialized; cmd_bt_bonds_clear in cdc_commands.c returns "bluetooth not running" when BTstack is not up.
Covered by this test: no. The guards run only when the CDC BT.STATUS or BT.BONDS.CLEAR commands call them, and neither scenario sends CDC commands. The usb2gc config-mode crash (#278) is not reproduced by either run.
Evidence: summary.json checks 13/13, failing_vs_main []; nrf_ble.console.txt shows normal BTstack start ("[BTSTACK_HOST] Starting BLE scan..."), so the guard is on the path but returns only when not initialized.
