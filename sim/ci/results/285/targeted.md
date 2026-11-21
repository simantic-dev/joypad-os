# PR 285 targeted: match the DualSense Edge on USB host
Verdict: DEMONSTRATED (driver match + decode). Re-run 2026-11-20 on the review simulator, native and PIO-USB hosts, real-descriptor DualSense peer under PID 0x0df2 (not an Edge dump). Details: review.md.
main: HID Gamepad, no EXT/touch frames, no OUT reports, idle triggers read 1. PR: Sony DualSense, 12 EXT frames (touch 65535/65535, then 32784/16392), 2 OUT reports (rumble/LED), triggers 0. Buttons/sticks identical on both.
Evidence: results/285/review/ (scenarios/285.sh). Earlier run: results/285/targeted/.
