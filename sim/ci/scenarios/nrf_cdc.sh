#!/bin/bash
# nrf_cdc.sh <nrf_elf> <outdir> <yaml> <wait_virtual_s> <cmd-json>... : bt2usb + scripted BLE pad(s); CDC host sends commands at <wait>.
ELF="$1"; OUT="$2"; Y="$3"; W="$4"; shift 4; D="$HOME/ahnaf/joypad-ci/scn/sim"
SIM=${SIM:-$HOME/dev/simantic/pyrite/.worktrees/ble-script-adv/target/release/sim}
mkdir -p "$OUT"; P=${NRF_USB_PORT:-47341}; cp "$ELF" "$D/elf/bt2usb_feather_nrf52840.elf"; cd "$D"
"$SIM" run --scenario "$Y" --timeout ${TIMEOUT:-9} --ascii --usb-raw joypad.usbd:$P --output "$OUT/console.txt" >"$OUT/sim.log" 2>&1 &
SP=$!; trap 'kill $SP 2>/dev/null' EXIT
n=0; until nc -z 127.0.0.1 $P 2>/dev/null; do kill -0 $SP 2>/dev/null || exit 1; n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2; done
python3 cdc_host.py $P "$W" "$@" | tee "$OUT/host.txt"; wait $SP
