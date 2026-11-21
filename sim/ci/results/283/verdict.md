# PR 283: docs(bt2n64): wire console power to VSYS, fix the 6-pin pinout
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 0 s (cached) / nRF 14 s; runs RP 33 s / nRF 14 s; behind_main 0
What the PR changes: docs/adapters/n64.md only: BT2N64 wiring table now uses VSYS for console power and the 3-pin N64 port pinout.
Covered by this test: no. Documentation only; no firmware file is touched.
Evidence: summary.json checks 13/13, failing_vs_main []; changed_file_count 1 (docs/adapters/n64.md).
