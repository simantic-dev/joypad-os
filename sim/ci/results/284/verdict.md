# PR 284: docs(dreamcast): button map matches the code since 7d086d4e
Result: not_exercised
Scenarios: RP2040 6/6 ok, nRF 7/7 ok (13/13), failing none; builds RP 0 s (cached) / nRF 14 s; runs RP 38 s / nRF 16 s; behind_main 0
What the PR changes: Dreamcast button-map docs (adapters/dreamcast.md, output/dreamcast.md) and a comment block in dreamcast_device.h updated to match map_buttons_to_dc(). No executable change.
Covered by this test: no. Only comments and markdown; the Dreamcast device is not part of either scenario (it is a usb2dc target, not usb2usb or bt2usb).
Evidence: summary.json checks 13/13, failing_vs_main []; touched_files rp2040 only (comment-only header); no code path changed.
