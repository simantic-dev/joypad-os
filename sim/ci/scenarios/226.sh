#!/bin/bash
# PR 226: usb2wiiext_pico. A DS4 (real descriptors) on the native USB host port; a Python Wii console (peers/wii_master.py) bit-bangs
# I2C on GP4/GP5 (SDA/SCL), 400 kHz, and polls the Classic Controller Pro registers. Data format 0x01 (default) and 0x03 (what the Wii menu selects).
# PR 226 only: main has no usb2wiiext target (the output stage wii_ext_device.c is on main, shipped by bt2wiiext on a Pico W, which this RP2040 model cannot run: CYW43 Bluetooth).
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/226/review"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-review}"
E=$("$S/build_wii.sh" 226 | tail -1)
"$S/run_wii.sh" ds4 0x054c 0x09cc "$E" "$R/fmt1" 12 1
"$S/run_wii.sh" ds4 0x054c 0x09cc "$E" "$R/fmt3" 12 3
