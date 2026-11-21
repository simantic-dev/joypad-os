#!/bin/bash
# PR 286 on the PIO-USB host build (joypad_usb_feather_rp2040, D+=GP16 D-=GP17): Switch 2 Pro, 281-byte config descriptor; bulk command 3 STALLed (once/always).
# Pico-PIO-USB reports a failed transfer per transfer, which the native RP2040 host driver (286.sh) cannot; needs a pyrite with USB.PioUsb (~/ahnaf/public-demos/bin/sim-piousb).
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/286/review"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-review}"
for ref in main 286; do E=$("$S/build_pio.sh" $ref | tail -1); for o in none once always; do "$S/run_pio.sh" sw2 0x057e 0x2069 "$E" "$R/pio_$o.$ref" 8 $o; done; done
