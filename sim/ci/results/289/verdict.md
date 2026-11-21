# PR 289: fix(3do): keep mouse motion the console hasn't polled yet
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 1 s, nRF 22 s, total 90 s
What the PR changes: `3do_device.c` accumulates unread mouse deltas into the next report with interrupts disabled.
Covered by this test: no. `3do_device.c` is not in the usb2usb or bt2usb builds (no 3do object in the RP2040 build dir), and the scenario has no 3DO console or mouse.
Evidence: `results/289/summary.json` result "pass", touched_files rp2040: src/native/device/3do/3do_device.c.
