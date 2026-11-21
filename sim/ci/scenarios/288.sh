#!/bin/bash
# PR 288: simple-mode router, mouse moves before it clicks.
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/288/targeted"; mkdir -p "$R"
for ref in main 288; do E=$("$S/build_b.sh" $ref | tail -1); "$S/run_host.sh" mouse 0x046d 0xc077 "$E" "$R/mouse.$ref" 3; done
