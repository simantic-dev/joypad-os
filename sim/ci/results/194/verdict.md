# PR 194: feat(nuon): add usb2nuon_rp2040zero target
Result: not_exercised
Scenarios: harness fixed (ps5default.cmake now forces PS5 only if the tree defines it); both builds now succeed (RP 6 s, nRF 8 s). nRF 7/7 ok. RP2040 0/6 on PS5-specific checks: the old base defaults to PS4 mode, so the device enumerates as 2e8a:10c6 not 2b81:0101; HOME/sign-request checks (PS5 P5General) cannot pass on this base. No fault.
What the PR changes: new usb2nuon_rp2040zero target (CMake, Makefile, workflow); no driver code.
Covered by this test: no. The RP scenario runs the base's default mode (PS4, not PS3), and the Nuon target is not built by the scenario. The 4 RP failures are base drift (behind_main 283), not PR-caused.
Evidence: results/194/refresh.peer.txt: "usb device 2e8a:10c6 ... 34 reports to console, 0 sign requests"; build errors from the earlier run (USB_OUTPUT_MODE_PS5 undeclared) are gone. nRF checks all ok.
