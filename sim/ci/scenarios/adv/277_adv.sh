#!/bin/bash
# PR 277 adversarial (sim-main, nRF bt2usb + scripted BLE pad, CDC host). results/277/adv/
#  race_<t>: BT.DISCOVERY.SET mode=2 sent t virtual s after boot, i.e. while the pad is being connected/paired (connect 1.046 s, paired 1.575 s);
#            then mode=0 at 4 s, BT.STATUS at 6.5 s. Pad must end connected (main has no such command: the baseline just connects).
#  fuzz:     BT.DISCOVERY.SET with -1, 3, 4294967297 (wraps to 1 in a 32-bit int?), "1" as a string, 1.9, missing mode; BT.STATUS after each.
C="$HOME/ahnaf/joypad-ci"; R="$C/results/277/adv"; mkdir -p "$R"; export SIM=${SIM:-$HOME/ahnaf/public-demos/bin/sim-main}
st='{"cmd":"BT.STATUS"}'
for ref in main 277; do E="$C/scn/elf/nrf_$ref.elf"
  for t in 1.06 1.15 1.3 1.45 1.7; do
    TIMEOUT=9 "$C/scenarios/nrf_cdc.sh" "$E" "$R/race_$t.$ref" nrf_ble.yaml $t '{"cmd":"BT.DISCOVERY.SET","mode":2}' 'wait:4' '{"cmd":"BT.DISCOVERY.SET","mode":0}' 'wait:6.5' "$st" >/dev/null 2>&1
  done
  TIMEOUT=7 "$C/scenarios/nrf_cdc.sh" "$E" "$R/fuzz.$ref" nrf_ble.yaml 3 '{"cmd":"BT.DISCOVERY.SET","mode":-1}' "$st" '{"cmd":"BT.DISCOVERY.SET","mode":3}' "$st" \
    '{"cmd":"BT.DISCOVERY.SET","mode":4294967297}' "$st" '{"cmd":"BT.DISCOVERY.SET","mode":"1"}' "$st" '{"cmd":"BT.DISCOVERY.SET","mode":1.9}' "$st" '{"cmd":"BT.DISCOVERY.SET"}' "$st" >/dev/null 2>&1
done
