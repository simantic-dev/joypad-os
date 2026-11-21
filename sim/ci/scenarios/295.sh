#!/bin/bash
# PR 295: autofire timing state. Switch-mode A, SELECT+B3 hold -> rapid-fire set -> tap B1 (30 Hz) -> hold B1. switchws = Switch default + WS2812_PIN=16 (the stock pico board has no NeoPixel, which leaves leds_is_indicating() true forever: firmware, not sim).
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/295/targeted"; mkdir -p "$R"
for ref in main 295; do E=$("$S/build_a.sh" $ref switchws | tail -1); "$S/run_a.sh" switch autofire "$E" "$R/af.$ref" 6.5; done
