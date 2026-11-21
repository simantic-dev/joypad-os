#!/bin/bash
# build_a.sh <ref> <ps3|switch> [noled]
# noled: harness-only patch for the autofire gesture (#295). In this sim build leds_is_indicating() never goes false after the
# gesture's LED indication (the NeoPixel state machine does not finish), which freezes runtime_profile_check_combo(); the patch
# drops that one condition, identically for main and the PR.
. "$HOME/ahnaf/joypad-ci/scenarios/common_b.sh"
checkout_ref "$1" >&2 || exit 1
if [ "$3" = noled ]; then
  sed -i '' 's/if (leds_is_indicating() || profile_indicator_is_active())/if (profile_indicator_is_active())/' "$WT/src/core/services/profiles/runtime_profile.c"
  touch "$WT/src/core/services/profiles/runtime_profile.c"
fi
build_a "$2"
