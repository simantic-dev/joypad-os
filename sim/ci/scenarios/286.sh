#!/bin/bash
# PR 286: Switch 2 Pro, 281-byte config descriptor; bulk command 3 STALLed (once/always). Native host half; the failed-bulk half is in 286_pio.sh.
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/286/review"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-review}"
for ref in main 286; do E=$("$S/build_b.sh" $ref | tail -1); for o in none once always; do "$S/run_host.sh" sw2 0x057e 0x2069 "$E" "$R/native_$o.$ref" 4 $o; done; done
