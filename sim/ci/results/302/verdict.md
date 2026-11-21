# PR 302: ci(nrf): pin build-nrf to ubuntu-24.04 (CMake 4 breaks NCS v3.1.0)
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), no failing checks vs main; build RP 2 s, nRF 23 s, total 93 s
What the PR changes: `.github/workflows/build.yml` pins only the `build-nrf` GitHub Actions job to ubuntu-24.04 (4 lines).
Covered by this test: no. The change affects the GitHub runner image for CI only. The simulator harness builds on the local lane, not through the workflow.
Evidence: `results/302/summary.json` result "pass", changed_file_count 1, touches all false.
