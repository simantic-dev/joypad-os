# PR 293: 3DO: make silly pad mode reachable again (#254)
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 3 s, nRF 17 s, total 105 s
What the PR changes: 3DO device reads the output mode from `profile_get_active_output_mode()`, usb23do declares Normal/Silly profile modes, and the unused `profile_set_output_mode_callback` API is removed from profile.c/h.
Covered by this test: no. `usb23do/app.c` and `3do_device.c` are not in the usb2usb or bt2usb builds. The profile.c/h removal is compiled into the RP2040 build (it builds), but nothing in the scenario uses that API.
Evidence: `results/293/summary.json` result "pass", touched_files rp2040: 3do_device.c; usb: src/apps/usb23do/*; no 3do object in the RP2040 build dir.
