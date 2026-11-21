# PR 288 adversarial: simple-mode router gives a mouse a slot on movement

Binary: sim-main, remapper B in SIMPLE router mode (main 9fa79f45 vs ci-pr-288). Script `scenarios/adv/288_adv.sh`; composite USB device from `scenarios/peers/usb_combo.py` (HID gamepad = instance 0, HID mouse = instance 1, option `swap`); the pad presses button 1 at poll 100 (about 0.84 s). Logs `results/288/adv/`.

| # | Attack | main | PR 288 |
|---|---|---|---|
| 1 | mouse interface silent (NAK) | Player 1 = gamepad (0.838 s) | same |
| 2 | mouse streams all-zero reports (idle chatter) from the first poll | Player 1 = gamepad (0.838 s), mouse never holds a slot | **Player 1 = HID Mouse at 0.639 s, gamepad becomes Player 2** (0.842 s) |
| 3 | mouse streams +-1 count jitter | same as main row 1 | **same as row 2: mouse takes Player 1** |

## Findings
**PR-INTRODUCED (medium): an idle mouse takes a player slot.** The new condition is `|| event->type == INPUT_TYPE_MOUSE`, with no check that anything moved, so every report from a mouse interface (all-zero chatter, sensor noise, a keyboard/dongle that exposes a mouse interface) claims the next free slot before any gamepad is touched; the pad is then Player 2, and on a one-slot output (usb2gc/wii style) it would get none. The PR's stated goal is "assign on movement". Repro: `results/288/adv/mousezero.288.console.txt` (`[0.638554s] Player 1 assigned: HID Mouse`, `[0.841826s] Player 2 assigned: HID Gamepad`) vs `mousezero.main.console.txt` (`Player 1 assigned: HID Gamepad`); confirmed twice, identical. Line: `router.c` `router_simple_mode`, the `event->type == INPUT_TYPE_MOUSE` term. Fix: require `event->delta_x || event->delta_y || event->wheel` (or buttons) for the mouse case.
Caveat: PR text says merge mode already behaves like this; the point is the new regression in simple mode, not a wrong comparison with merge.
Side observation (not the PR): with the pad as HID instance 1 (default ordering of `usb_combo.py`, no `swap`) the generic gamepad is polled once and never again while the mouse on instance 0 keeps being polled (`peer.log`: `poll ep 2 1`, then nothing). Not investigated whether this is firmware (hid re-arm for instance 1) or the simulator's RP2040 host scheduling of a second interrupt endpoint; same on main.
