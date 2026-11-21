#!/bin/bash
# 290.sh <nrf_elf> <outdir> : Xbox-VID BLE pad (DIS PnP 045E:0B13, output report 3 write-with-response, response delayed 150 ms)
#  + USB host sending haptic START then STOP 20 virtual ms later (second write arrives while first is in flight).
ELF="$1"; OUT="$2"; D="$HOME/ahnaf/joypad-ci/scn/sim"; SIM=${SIM:-$HOME/dev/simantic/pyrite/.worktrees/ble-script-adv/target/release/sim}
mkdir -p "$OUT"; P=${NRF_USB_PORT:-47321}; cp "$ELF" "$D/elf/bt2usb_feather_nrf52840.elf"; cd "$D"
"$SIM" run --scenario nrf_ble_xbox.yaml --timeout 10 --ascii --usb-raw joypad.usbd:$P --output "$OUT/console.txt" >"$OUT/sim.log" 2>&1 &
SP=$!; trap 'kill $SP 2>/dev/null' EXIT
n=0; until nc -z 127.0.0.1 $P 2>/dev/null; do kill -0 $SP 2>/dev/null || exit 1; n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2; done
python3 xbox_rumble_host.py $P 60 4 | tee "$OUT/host.txt"; wait $SP
grep -hE "rumble write|write response|send_write_report|Xbox|DIS PnP|BTHID_GAMEPAD\] Parsed" "$OUT/sim.log" "$OUT/console.txt" | head -30 > "$OUT/evidence.txt"; cat "$OUT/evidence.txt"
