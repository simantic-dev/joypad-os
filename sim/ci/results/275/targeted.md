# PR 275 targeted: DS4 touchpad normalization, calibration request, Nacon Revolution Pro 2 (146b:0d02)
Verdict: DEMONSTRATED. Re-run 2026-11-20 with the real-descriptor DS4 peer on the review simulator (sim-review: main + PIO-USB branches). Details and caveats: review.md.
Touch (1919,941): main 1919/941, PR 65535/65465. Two fingers: main 960,480/471,235; PR 32784,16392/32767,16348. Nacon 146b:0d02: main HID Gamepad (no touch), PR Sony DualShock 4. GET_REPORT 0x02 sent by the PR only (DS4 answers 37 bytes, Nacon stalls).
Evidence: results/275/review/ (scenarios/275.sh). Earlier run (hand-written peer): results/275/targeted/.
