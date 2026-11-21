#!/bin/sh
# joypad-mcp -> UART0 pty -> stock Joypad usb2usb (Feather RP2040 USB host build, CONFIG_UART_HOST) on the simulated RP2040 -> USB console host
cd "$(dirname "$0")"; SIM=${SIM:?}; ELF=${ELF:?}; MCP=${MCP:?}; P=${USB_PORT:-47120}; T=${SECS:-20}
"$SIM" RP2040 run --elf "$ELF" --timeout $T --ascii --usb-raw usb:$P --uart-pty uart0 --output console.txt > sim.log 2>&1 &
S=$!; trap 'kill $S 2>/dev/null' EXIT
n=0; until nc -z 127.0.0.1 $P 2>/dev/null && grep -q /dev/ sim.log; do kill -0 $S 2>/dev/null || { cat sim.log; exit 1; }; n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2; done
PTY=$(grep -o '/dev/[a-z0-9/]*' sim.log | head -1); echo "uart0 is on $PTY"
python3 switch_host.py $P $T > console_host.txt 2>&1 &
sleep 1; node mcp_drive.mjs "$MCP/dist/server.js" "$PTY"
wait $S; echo "--- console host"; cat console_host.txt
