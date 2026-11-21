#!/bin/bash
# run_wii.sh <kind> <vid> <pid> <elf> <outprefix> [seconds] [fmt]   usb2wiiext_pico: USB pad on the native host port, Wii console (peers/wii_master.py) bit-banging I2C on GP4/GP5.
D="$(cd "$(dirname "$0")" && pwd)"; SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-review}"
KIND=$1; VID=$2; PID=$3; ELF=$4; P=$5; SECS=${6:-12}; FMT=${7:-1}; STEP=${STEP_NS:-833}
{ echo "VID=$VID; PID=$PID; KIND='$KIND'; OPT=''"; cat "$D/peers/usb_head.py" "$D/peers/usb_$KIND.py"; grep -q "^class Device" "$D/peers/usb_$KIND.py" || printf "\nclass Device(Base):\n    pass\n"; } > "$P.device.py"
{ [ -n "${NODEV:-}" ] || printf 'dev: USB.ScriptedUsbDevice @ usb\n    file: "%s"\n' "$P.device.py"; cat <<R

i2c0:
    pinLevel: true

wii: Scripted.ScriptedGpioPeer @ none
    file: "$D/peers/wii_master.py"
    config: "{\"fmt\": $FMT, \"step_ns\": $STEP, \"gap_us\": ${GAP_US:-0}, \"start_ms\": ${START_MS:-1500}, \"poll_ms\": ${POLL_MS:-16.6}}"
    numberOfGpios: 2
    0 -> gpio0@36
    1 -> gpio0@37

gpio0:
    4 -> wii@0
    5 -> wii@1
R
} > "$P.board.repl"
"$SIM" RP2040 run --elf "$ELF" --board "$P.board.repl" --timeout "$SECS" --ascii --output "$P.console.txt" > "$P.sim.log" 2>&1
grep usbpeer "$P.sim.log" > "$P.peer.log"; grep wiimaster "$P.sim.log" > "$P.wii.log"
