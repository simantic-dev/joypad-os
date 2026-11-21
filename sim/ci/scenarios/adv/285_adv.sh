#!/bin/bash
# PR 285 adversarial: DualSense Edge 054c:0df2 with Edge-only paddle/Fn bits, truncated reports.  sim-main, native host. results/285/adv/
S="$(cd "$(dirname "$0")/.." && pwd)"; R="$HOME/ahnaf/joypad-ci/results/285/adv"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-main}"
for ref in main 285; do E=$("$S/build_b.sh" $ref | tail -1); for o in none paddle short zero; do "$S/run_host.sh" ds5 0x054c 0x0df2 "$E" "$R/$o.$ref" 10 $o; done; done
