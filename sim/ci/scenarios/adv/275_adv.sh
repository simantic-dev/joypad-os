#!/bin/bash
# PR 275 adversarial: touch values past the pad range, calibration reply sizes. sim-main, native host.  results/275/adv/
S="$(cd "$(dirname "$0")/.." && pwd)"; R="$HOME/ahnaf/joypad-ci/results/275/adv"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-main}"
for ref in main 275; do E=$("$S/build_b.sh" $ref | tail -1)
  for o in none touchmax calbig calshort calempty calstall; do
    "$S/run_host.sh" ds4 0x054c 0x09cc "$E" "$R/$o.$ref" 16 "$o"; done; done
