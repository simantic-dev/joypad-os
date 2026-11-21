# PR 203 targeted: authentic 49-byte DualShock 3 input report
Verdict: DEMONSTRATED (PR merged onto current main; the PR itself is 379 commits behind main). PS3 mode, --usb-hid-tap usb, review simulator. Details: review.md.
main: 50-byte report, motion at 42-49. PR on main: 49 bytes, motion at 41-48 (hid-sony.c SIXAXIS_INPUT_REPORT_ACC_X_OFFSET = 41, size 49 check). Bytes 0-40 identical.
Evidence: results/203/review/ps3.{main,203,203m}.console.txt (scenarios/203.sh).
