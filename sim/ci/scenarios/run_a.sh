#!/bin/bash
# run_a.sh <ps3|switch> <sticks|capture|autofire> <elf> <outprefix> [seconds]   remapper A with a scripted USB console + uart_peer feeder
D="$(cd "$(dirname "$0")" && pwd)"; SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-0.10.5}"
export JP_SIM_DIR="$HOME/ahnaf/joypad-ci/wt/lane-a/sim"
MODE=$1; SC=$2; ELF=$3; P=$4; SECS=${5:-6}; UP=${USB_PORT:-47241}; LP=${UART_PORT:-47242}
"$SIM" RP2040 run --elf "$ELF" --timeout "$SECS" --ascii --usb-raw usb:$UP --uart-tcp uart1:$LP --output "$P.console.txt" > "$P.sim.log" 2>&1 &
SP=$!; trap 'kill $SP 2>/dev/null' EXIT
n=0; until nc -z 127.0.0.1 $UP 2>/dev/null && nc -z 127.0.0.1 $LP 2>/dev/null; do kill -0 $SP 2>/dev/null || { cat "$P.sim.log"; exit 1; }; n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2; done
python3 "$D/a_peer.py" $UP $LP $MODE $SC > "$P.reports.txt" 2>&1; wait $SP
