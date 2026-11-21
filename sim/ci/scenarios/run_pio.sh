#!/bin/bash
# run_pio.sh <kind> <vid> <pid> <elf> <outprefix> [seconds] [opt]   RP2040 usb2usb with the Pico-PIO-USB host (D+=GP16 D-=GP17) and a scripted USB device on those pads
# kind = ds4 | ds5 | sw2 | mouse; OPT is passed to the kind file (sw2: once|always|none = how bulk command 3 fails)   -> outprefix.{console,sim.log,peer.log}.txt
# SIM = a pyrite build with USB.PioUsb (default ~/ahnaf/public-demos/bin/sim-piousb); PIOUSB_ARGS = one extra board key, e.g. "turnaroundNs: 600"
D="$(cd "$(dirname "$0")" && pwd)"; SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-piousb}"
KIND=$1; VID=$2; PID=$3; ELF=$4; P=$5; SECS=${6:-4}; OPT=${7:-}
{ echo "VID=$VID; PID=$PID; KIND='$KIND'; OPT='$OPT'"; cat "$D/peers/usb_head.py" "$D/peers/usb_$KIND.py"; grep -q "^class Device" "$D/peers/usb_$KIND.py" || printf "\nclass Device(Base):\n    pass\n"; } > "$P.device.py"
{ echo "piousb: USB.PioUsb @ none"; [ -n "$PIOUSB_ARGS" ] && echo "    $PIOUSB_ARGS"
  printf 'gpio0:\n    16 -> piousb@0 | pio0@16 | pio1@16\n    17 -> piousb@1 | pio0@17 | pio1@17\n\npiousb:\n    0 -> gpio0@48\n    1 -> gpio0@49\n\ndev: USB.ScriptedUsbDevice @ piousb\n    file: "%s"\n' "$P.device.py"; } > "$P.board.repl"
"$SIM" ${SIM_FLAGS:-} RP2040 run ${RUN_FLAGS:-} --elf "$ELF" --board "$P.board.repl" --timeout "$SECS" --ascii --output "$P.console.txt" > "$P.sim.log" 2>&1
grep usbpeer "$P.sim.log" > "$P.peer.log"
