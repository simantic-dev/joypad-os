# PR 304: add stadia controller to list of BLE controllers
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 5 s, nRF 38 s, total 172 s
What the PR changes: adds a Stadia controller line to docs/adapters/bluetooth.md (2 lines).
Covered by this test: no. Docs only; no code is compiled or run.
Evidence: `results/304/summary.json` result "pass", changed_file_count 1, touched_files bt: docs/adapters/bluetooth.md.
