#!/bin/bash
# PR 203: PS3 output mode (remapper A, ps3default.cmake); device-side HID IN reports via --usb-hid-tap usb for main, the PR as submitted (203, 379 commits behind main) and the PR merged onto current main (203m = local merge, only ps3_descriptors.h differs from main).
# Inputs come over the uart_peer link (a_feed.py): Cross, left stick up-right, right stick down-left, Cross+L2.
S="$(cd "$(dirname "$0")" && pwd)"; R="$HOME/ahnaf/joypad-ci/results/203/review"; mkdir -p "$R"
export SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-review}" JP_SIM_DIR="$HOME/ahnaf/joypad-ci/wt/lane-a/sim"
for ref in main 203 203m; do E=$("$S/build_a.sh" $ref ps3 | tail -1); P="$R/ps3.$ref"; LP=${UART_PORT:-47242}
  "$SIM" RP2040 run --elf "$E" --timeout 6 --ascii --usb-hid-tap usb --uart-tcp uart1:$LP --output "$P.console.txt" > "$P.sim.log" 2>&1 &
  SP=$!; n=0; until nc -z 127.0.0.1 $LP 2>/dev/null; do kill -0 $SP 2>/dev/null || { cat "$P.sim.log"; break; }; n=$((n+1)); [ $n -gt 300 ] && break; sleep 0.2; done
  python3 "$S/a_feed.py" $LP > "$P.feed.txt" 2>&1; wait $SP
done
