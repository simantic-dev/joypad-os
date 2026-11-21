#!/bin/bash
# PR 296: Switch mode SELECT+START -> Capture.
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/296/targeted"; mkdir -p "$R"
for ref in main 296; do E=$("$S/build_a.sh" $ref switch | tail -1); "$S/run_a.sh" switch capture "$E" "$R/capture.$ref" 3; done
