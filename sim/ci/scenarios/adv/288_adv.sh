#!/bin/bash
# PR 288 adversarial (sim-main, remapper B in SIMPLE router mode): composite USB device = HID mouse + HID gamepad on the one native host port.
# (swap: pad = HID instance 0, mouse = instance 1; with the pad as instance 1 the sim polls it once only, see 288/adversarial.md.) The mouse interface sends idle chatter (all-zero reports / +-1 jitter); the pad presses a button at poll 100. Who gets Player 1?  results/288/adv/
S="$(cd "$(dirname "$0")/.." && pwd)"; R="$HOME/ahnaf/joypad-ci/results/288/adv"; mkdir -p "$R"; export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-main}"
for ref in main 288; do E=$("$S/build_b.sh" $ref | tail -1); for o in quiet mousezero mousejit; do "$S/run_host.sh" combo 0x1234 0x5678 "$E" "$R/$o.$ref" 4 swap,$o; done; done
