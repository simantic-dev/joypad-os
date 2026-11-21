# PR 295: fix(profile): keep autofire timing state alive across profile_apply calls
Result: pass
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 2 s, nRF 23 s, total 133 s
What the PR changes: makes the profile output structs static (per-player) in gamecube, n64, nuon, 3do, loopy, and carries per-player autofire state in `apply_usbd_profile_player()` in usbd.c; `profile_apply_button_map` zero-inits its output.
Covered by this test: partly. `usbd.c` is compiled into both builds and `apply_usbd_profile_player()` runs on every USB device report in the RP2040 (PS5 output) and nRF (bt2usb) runs, so the new memcpy path executes and nothing faults. The autofire behaviour itself is not observed: the scenario does not map any autofire button, so the carried state never changes an output. The gamecube, n64, nuon, 3do and loopy edits are in files not built into either target.
Evidence: `results/295/summary.json` result "pass", failing_vs_main []; touched_files usb: src/usb/usbd/usbd.c (built into both: usbd.c.o present in RP2040 and nRF object dirs).
