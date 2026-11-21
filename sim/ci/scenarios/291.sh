#!/bin/bash
# PR 291: PS3 mode square sticks. Remapper A built with PS3 as the default USB mode.
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/291/targeted"; mkdir -p "$R"
for ref in main 291; do E=$("$S/build_a.sh" $ref ps3 | tail -1); "$S/run_a.sh" ps3 sticks "$E" "$R/sticks.$ref" 3; done
