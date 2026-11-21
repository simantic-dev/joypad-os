# PR 277: feat(bt): stop the central from grabbing every controller in the room
Result: pass
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 2 s / nRF 15 s; runs RP 35 s / nRF 8 s; behind_main 0
What the PR changes: BTstack central gets a discovery policy (AUTO/BONDED/OFF) restored from flash at init, a btstack_host_start_scan_explicit() that the user-requested scan uses, bond-gated auto-connect, and BT.DISCOVERY.SET/GET over CDC; ESP and nRF flash_*.c gain the setter/getter.
Covered by this test: partly. The nRF bt2usb central runs the changed btstack_host.c at default (AUTO) mode: the boot scan starts and the pad is discovered, paired and its inputs arrive (summary nRF checks 7/7). The BONDED and OFF modes, the bond-gated connect and the BT.DISCOVERY.SET CDC command are not run. The ESP and web-config parts are not built here.
Evidence: nrf_ble.console.txt "[BTSTACK_HOST] Starting BLE scan..." then "[BTSTACK_HOST] Requesting pairing..."; summary.json checks 13/13, failing_vs_main []; touched_files include nrf/src/flash_nrf.c and src/bt/btstack/btstack_host.c.
