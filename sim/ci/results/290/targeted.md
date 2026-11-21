# PR 290 targeted: retry Xbox rumble when a BLE write is still in flight
Scenario: scenarios/290.sh (scn/sim/peers/ble_xbox.py + nrf_ble_xbox.yaml + xbox_rumble_host.py). nRF bt2usb on pyrite (ble-script-adv sim, Peer.adv_data). Scripted BLE pad named "Xbox Wireless Controller", DIS PnP 045E:0B13, HOGP output report 3 (8 bytes) writable WITH response only, response held 150 ms. USB host sends SInput haptic START (amp 255) then STOP (amp 0) 25 virtual ms later, i.e. while the first ATT write is unacked.
Main: stop is lost. Firmware logs `BLE send_write_report failed: report_id=0x03 status=0x0C` (COMMAND_DISALLOWED) and never resends. Pad sees ONE write: `0300006464ff0000` (start, motors 100/100, duration 0xFF).
PR: pad sees TWO writes: `0300006464ff0000` then `0300000000ff0000` (stop), the second sent after the first write response. No error log line.
Verdict: FIX DEMONSTRATED (dropped stop is retried; the motor-keeps-running cause is reproduced on main). Not shown: the 0xFF duration unit, real pad behaviour.
Evidence: results/290/targeted/{main,pr}_{sim.log,console.txt,host.txt}
  main console: [3.535957s] BTSTACK_HOST BLE send_write_report failed: report_id=0x03 status=0x0C ; main sim.log: one "[pad] rumble write from Joypad: 0300006464ff0000"
  pr sim.log: "rumble write ... 0300006464ff0000", "write response sent", "rumble write ... 0300000000ff0000"
Note: the stale-stack-buffer half of the PR (static per-connection copy) is not observable here (pad acks promptly with right bytes either way).
