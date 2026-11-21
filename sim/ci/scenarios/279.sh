#!/bin/bash
# 279.sh <gc_elf> <outdir> : usb2gc_rp2040zero (joypad_ngc_rp2040zero) boots with no GameCube console -> CDC config mode,
# BTstack never started; USB host sends BT.STATUS then BT.BONDS.CLEAR then PROFILE.LIST (must still answer after the first two).
ELF="$1"; OUT="$2"; D="$HOME/ahnaf/joypad-ci/scn/sim"; SIM=${SIM:-$HOME/ahnaf/public-demos/bin/sim-0.10.5}
mkdir -p "$OUT"; P=${NRF_USB_PORT:-47331}; cd "$D"
"$SIM" RP2040 run --elf "$ELF" --timeout 12 --ascii --usb-raw usb:$P --output "$OUT/console.txt" >"$OUT/sim.log" 2>&1 &
SP=$!; trap 'kill $SP 2>/dev/null' EXIT
n=0; until nc -z 127.0.0.1 $P 2>/dev/null; do kill -0 $SP 2>/dev/null || { cat "$OUT/sim.log"; exit 1; }; n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2; done
python3 cdc_host.py $P 2 '{"cmd":"BT.STATUS"}' '{"cmd":"BT.BONDS.CLEAR"}' '{"cmd":"PROFILE.LIST"}' | tee "$OUT/host.txt"; wait $SP
grep -iE "fault|panic|assert|hard" "$OUT/sim.log" "$OUT/console.txt" | head -5
