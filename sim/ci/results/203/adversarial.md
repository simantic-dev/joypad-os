# PR 203 adversarial: authentic 49-byte DualShock 3 input report

Static/offline only, no sim run: the harness build for 203 fails (PS5-mode forcing on an old base, results/203/verdict.md) and PS3 mode needs a PS3 USB host peer.
Checks done: (1) parsed `ps3_report_descriptor[]` of main and of the PR with a HID item parser: report id 1 input = 49 data bytes on main (+ id = 50) and 48 data bytes on the PR (+ id = 49), matching `sizeof(ps3_in_report_t)` (49) in the PR and the new `_Static_assert`; output and the four feature reports unchanged (48 bytes). (2) `ps3_mode_send_report` sends `sizeof(ps3_report)` with id 0 (the id is in the struct), so the transfer is 49 bytes, within the 64-byte endpoint. (3) `ps3_mode_handle_output`'s `len == 49 && data[0] == 1` heuristic is on the OUT path and unaffected.
Attacks not run: PS3 GET_REPORT(Input, 1) by a host that expects 50 bytes (the WebHID motion alignment the old padding served); a host-side parse at offset 41 (shown correct in results/203/targeted.md).
Findings: none (NONE). Risk to note: the old 50th byte existed so WebHID motion lined up; the PR removes it deliberately.
