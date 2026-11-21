#!/bin/bash
# PR 226 adversarial (usb2wiiext_pico on sim-main): Wii master probing at boot (start_ms=2, before USB enumeration), master polling at ~1 ms,
# and no pad attached at all. PR-only target (main has no usb2wiiext). results/226/adv/
S="$(cd "$(dirname "$0")/.." && pwd)"; R="$HOME/ahnaf/joypad-ci/results/226/adv"; mkdir -p "$R"; export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-main}"
E=$("$S/build_wii.sh" 226 | tail -1)
START_MS=2    "$S/run_wii.sh" ds4 0x054c 0x09cc "$E" "$R/early" 6 1
POLL_MS=1     "$S/run_wii.sh" ds4 0x054c 0x09cc "$E" "$R/fastpoll" 8 1
NODEV=1       "$S/run_wii.sh" ds4 0x054c 0x09cc "$E" "$R/nopad" 4 1
