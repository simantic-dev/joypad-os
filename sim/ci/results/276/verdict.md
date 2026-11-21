# PR 276: docs(usbd): correct PS4 and Switch output-mode VID:PID
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 2 s / nRF 18 s; runs RP 32 s / nRF 11 s; behind_main 0
What the PR changes: docs only. The USB output-mode tables now list HORI IDs (0F0D:0086 PS4, 0F0D:0092 Switch) instead of Sony and Nintendo IDs.
Covered by this test: no. Documentation only; the firmware descriptors are not changed.
Evidence: summary.json checks 13/13, failing_vs_main []; changed_file_count 2 (docs/adapters/usb.md, docs/output/usb-device.md).
