# PR 294: feat(gc): pressure-sensitive analog A/B in GameCube analog modes (#114)
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 4 s, nRF 21 s, total 84 s
What the PR changes: new `profile_inputs_for_output()` in profile.c/h, used by gamecube_device.c to fill GC analog A/B bytes from pressure in poll modes 0, 1, 2 and 4.
Covered by this test: no. profile.c is compiled into both builds, but the only caller is `gamecube_device.c`, which is not part of the usb2usb or bt2usb targets (no gamecube object in the RP2040 build dir), so the new function is never called.
Evidence: `results/294/summary.json` result "pass", touched_files rp2040: src/native/device/gamecube/gamecube_device.c (not in build objects).
