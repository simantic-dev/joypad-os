#!/bin/bash
# PR 285: DualSense Edge (054c:0df2) on the USB host, main vs PR, native host (remapper B) and PIO-USB host (joypad_usb_feather_rp2040).
# Peer: usb_ds5.py (real DualSense descriptors from public dumps) under the Edge PID; no public Edge descriptor dump was used, see review.md.
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/285/review"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-review}"
for ref in main 285; do E=$("$S/build_b.sh" $ref | tail -1); "$S/run_host.sh" ds5 0x054c 0x0df2 "$E" "$R/native.$ref" 12; done
for ref in main 285; do E=$("$S/build_pio.sh" $ref | tail -1); RUN_FLAGS="--usb-hid-tap usb" "$S/run_pio.sh" ds5 0x054c 0x0df2 "$E" "$R/pio.$ref" 12; done
