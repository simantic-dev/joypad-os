# PR 277 targeted: discovery policy (stop the central grabbing every controller)
Scenario: scenarios/277.sh (nRF bt2usb + scripted BLE pad from sim-ble-python, CDC host scn/sim/cdc_host.py). Pad connects under AUTO; host sets BT.DISCOVERY.SET mode=2 (OFF), then BLE.DROP 1000 ms, then waits.
Main: command unknown (`{"ok":false,"error":"unknown command"}`); after the drop holdoff the central rescans (`[4.021s] Starting BLE scan...`, `[4.07s] Connecting to Generic BLE Gamepad`) and BT.STATUS at t=7.5 s shows connections:1.
PR: `Discovery mode: OFF` logged at 3.007 s, BT.STATUS reports "discovery":2, no rescan, no reconnect, connections:0 at t=7.5 s.
Verdict: FEATURE DEMONSTRATED for the OFF mode on the BLE path only (new CDC command, no background scan after OFF, status field).
Could not simulate: the headline case (Classic BR/EDR inquiry auto-connecting to any gamepad-shaped CoD; BONDED mode with link-key filter; LIAC-only inquiry; "pad in next room"). nRF has no ENABLE_CLASSIC and pyrite has no BR/EDR radio, so those lines are compiled out / unreachable. BONDED and the explicit-scan exemption (BT.SCAN) are also untested (BT.SCAN not in the bt2usb build). Two-advertising-pads test not applicable: BLE path unchanged for AUTO/BONDED.
Evidence: results/277/targeted/{main,pr}_{console.txt,host.txt}
