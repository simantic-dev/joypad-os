#!/bin/sh
# usage: sim/run.sh <change|refresh|stream>   (SIM=path to sim, default: sim on PATH)
# Boots the usb2usb remapper-A image on the released sim's RP2040 and plays the
# USB console host, B, the dongle and the gamepad around it (peer.py).
cd "$(dirname "$0")" || exit 1
SIM=${SIM:-sim}; MODE=${1:-refresh}; OUT=${OUT:-out}; mkdir -p "$OUT"
USB_PORT=${USB_PORT:-47101}; UART_PORT=${UART_PORT:-47102}
"$SIM" RP2040 run --elf elf/a_ps5default_2145ffa8.elf --timeout 8 --ascii \
    --usb-raw usb:$USB_PORT --uart-tcp uart1:$UART_PORT \
    --usb-capture "usb:$OUT/$MODE.pcap" --output "$OUT/$MODE.console.txt" >"$OUT/$MODE.sim.log" 2>&1 &
SIM_PID=$!
trap 'kill $SIM_PID 2>/dev/null' EXIT
n=0
until nc -z 127.0.0.1 $USB_PORT 2>/dev/null && nc -z 127.0.0.1 $UART_PORT 2>/dev/null; do
    kill -0 $SIM_PID 2>/dev/null || { cat "$OUT/$MODE.sim.log"; exit 1; }
    n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2
done
REPORT_LOG="$OUT/$MODE.reports.csv" python3 peer.py $USB_PORT $UART_PORT "$MODE" | tee "$OUT/$MODE.peer.txt"
