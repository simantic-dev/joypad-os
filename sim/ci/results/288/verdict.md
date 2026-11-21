# PR 288: fix(router): give a mouse a player slot on movement in simple mode
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 3 s, nRF 31 s, total 132 s
What the PR changes: in `router_simple_mode()`, a `INPUT_TYPE_MOUSE` event now allocates a player slot on movement, not only on a button press.
Covered by this test: no. `router.c` is compiled into both builds, so the new condition is evaluated, but it only changes behaviour for a mouse input. The scenario has a gamepad and a console only, no USB mouse.
Evidence: `results/288/summary.json` result "pass", touches all false, touched_files {} (diff is router.c only, 4 lines).
