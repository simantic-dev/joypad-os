# PR 203: fix(ps3): restore the authentic 49-byte DualShock 3 input report
Result: not_exercised
Scenarios: harness fixed (ps5default.cmake now forces PS5 only if the tree defines it); both builds now succeed (RP 8 s, nRF 13 s). nRF 7/7 ok. RP2040 0/6 on PS5-specific checks: the old base defaults to PS4 mode, so the device enumerates as 2e8a:10c6 not 2b81:0101; HOME/sign-request checks (PS5 P5General) cannot pass on this base. No fault.
What the PR changes: ps3_descriptors.h: PS3 input report 50 -> 49 bytes, padding removed from the descriptor, collection types match a real DS3.
Covered by this test: no. The RP scenario runs the base's default mode (PS4, not PS3), and the PS3 descriptor is not the active mode. The 4 RP failures are base drift (behind_main 379), not PR-caused.
Evidence: results/203/refresh.peer.txt: "usb device 2e8a:10c6 ... 34 reports to console, 0 sign requests"; build errors from the earlier run (USB_OUTPUT_MODE_PS5 undeclared) are gone. nRF checks all ok.
