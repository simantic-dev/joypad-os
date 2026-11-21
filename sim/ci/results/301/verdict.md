# PR 301: docs(changelog): fold Unreleased into 2.5.0 ahead of the release
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 1 s, nRF 15 s, total 89 s
What the PR changes: moves the Unreleased CHANGELOG entries under a 2.5.0 heading (CHANGELOG.md only, no code).
Covered by this test: no. Changelog only; nothing compiled or run.
Evidence: `results/301/summary.json` result "pass", changed_file_count 1, touches all false.
