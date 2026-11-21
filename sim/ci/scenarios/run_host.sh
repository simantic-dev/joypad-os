#!/bin/bash
# run_host.sh <kind> <vid> <pid> <elf> <outprefix> [seconds] [opt]   remapper B (native USB host) with a scripted USB device on its port
# kind = ds4 | ds5 | sw2 | mouse; OPT is passed to the kind file (sw2: once|always|none = how bulk command 3 fails)   -> outprefix.{console,sim.log,peer.log,link}.txt
D="$(cd "$(dirname "$0")" && pwd)"; SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-0.10.5}"
KIND=$1; VID=$2; PID=$3; ELF=$4; P=$5; SECS=${6:-4}; OPT=${7:-}; PORT=${UART_PORT:-47231}
{ echo "VID=$VID; PID=$PID; KIND='$KIND'; OPT='$OPT'"; cat "$D/peers/usb_head.py" "$D/peers/usb_$KIND.py"; grep -q "^class Device" "$D/peers/usb_$KIND.py" || printf "\nclass Device(Base):\n    pass\n"; } > "$P.device.py"
printf 'dev: USB.ScriptedUsbDevice @ usb\n    file: "%s"\n' "$P.device.py" > "$P.board.repl"
"$SIM" RP2040 run --elf "$ELF" --board "$P.board.repl" --timeout "$SECS" --ascii --uart-tcp uart1:$PORT --output "$P.console.txt" > "$P.sim.log" 2>&1 &
SP=$!; trap 'kill $SP 2>/dev/null' EXIT
n=0; until nc -z 127.0.0.1 $PORT 2>/dev/null; do kill -0 $SP 2>/dev/null || { cat "$P.sim.log"; exit 1; }; n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2; done
python3 "$D/host_peer.py" $PORT $SECS > "$P.link.txt" 2>&1; wait $SP
grep usbpeer "$P.sim.log" > "$P.peer.log"
