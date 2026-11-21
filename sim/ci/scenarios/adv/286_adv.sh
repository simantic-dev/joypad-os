#!/bin/bash
# PR 286 adversarial (native host, sim-main): bulk cmd NAKed forever, interface 1 past 256 bytes, zero-length descriptor.  results/286/adv/
S="$(cd "$(dirname "$0")/.." && pwd)"; R="$HOME/ahnaf/joypad-ci/results/286/adv"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-main}"
for ref in main 286; do E=$("$S/build_b.sh" $ref | tail -1); for o in none nak late1 zerolen always; do "$S/run_host.sh" sw2 0x057e 0x2069 "$E" "$R/$o.$ref" 5 $o; done; done
