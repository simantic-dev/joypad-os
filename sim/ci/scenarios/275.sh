#!/bin/bash
# PR 275: DS4 touch normalization + Nacon Revolution Pro 2 (146b:0d02) + calibration request (0x02 GET_REPORT at mount).
# Peers: real-descriptor DS4 (usb_ds4.py). Nacon = the same DS4 peer under 146b:0d02 with 0x02 stalled and accel=0 until requested.
# Touch phases (usb_ds4.py): finger 1 far corner 12-13 s, then two fingers 13-14 s; run 16 s. Needs SIM=sim-review.
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/275/review"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-review}"
for ref in main 275; do E=$("$S/build_b.sh" $ref | tail -1)
  "$S/run_host.sh" ds4 0x054c 0x09cc "$E" "$R/ds4_09cc.$ref" 16; "$S/run_host.sh" ds4 0x146b 0x0d02 "$E" "$R/nacon.$ref" 16; done
