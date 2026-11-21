# PR 285 adversarial: DualSense Edge (054c:0df2) on the DS5 USB host driver

Binary: sim-main, native host, remapper B (main 9fa79f45 vs ci-pr-285). Script `scenarios/adv/285_adv.sh`, options in `scenarios/peers/usb_ds5.py`. Logs `results/285/adv/`.
The whole PR is one PID line in `is_sony_ds5()`; the stress is on what the DS5 driver then does with Edge-specific data.

| # | Attack | main | PR 285 |
|---|---|---|---|
| 1 | baseline Edge | `DEVICE:[HID Gamepad]`, no touch/motion | `DEVICE:[Sony DualSense]`, auth registered, Player 1 |
| 2 | Edge paddle / Fn bits (byte 10 bits 6,7,4,5) held one second each, nothing else changing | generic HID, no player | **no event at all, no player assigned** until the next normal input (2.40 s vs 1.40 s) |
| 3 | 10-byte input report (truncated) | generic HID | no fault, no event (driver memcpys 63 bytes from the host buffer, stale bytes) |
| 4 | 1-byte report (id only) | generic HID | no fault, no event |

## Findings
**PR-INCOMPLETE (low-medium): Edge-only buttons are dropped.** `sony_ds5_report_t` byte 10 = `ps:1 tpad:1 mute:1 counter:5`. On an Edge, bits 4-7 of that byte carry the Fn and paddle buttons (per SDL's PS5 driver, from memory, not re-checked against a dump). The driver treats them as the frame counter: `prev_report.counter = ds5_report.counter` hides them from `diff_report_ds5`, and no `JP_BUTTON_*` is mapped. Result: a paddle press produces no router event and does not even assign the player. Repro: `OPT=paddle` -> `results/285/adv/paddle.285.{console,link}.txt` (`Player 1 assigned` at 2.399 s, vs 1.399 s in `none.285`; no EVENT with buttons!=0 during the paddle window). Suggested fix: when `pid==0x0df2`, map `buttons2 & 0x10/0x20/0x40/0x80` to L4/R4/L5/R5 (or A-buttons) and mask them out of the counter compare. Caveat: the peer's Edge byte-10 layout is the DualSense layout plus the SDL paddle bits, not an Edge dump.

Attacks 3 and 4: PRE-EXISTING behaviour of the driver (no `len` check before `memcpy`); harmless in the sim because TinyUSB's host buffer is 64 bytes, but the PR newly routes Edge pads into it.
