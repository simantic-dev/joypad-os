#!/bin/bash
# PR 290 adversarial (sim-main, nRF bt2usb + scripted Xbox BLE pad). Cases: write response held N ticks of 50 ms, USB host START/STOP pair or flood.
# usage: 290_adv.sh   -> results/290/adv/<case>.<ref>.{pad,host,console}.txt     case = h3pair h16pair h3flood h40pair
C="$HOME/ahnaf/joypad-ci"; D="$C/scn/sim"; R="${OUT:-$C/results/290/adv}"; mkdir -p "$R"; SIM=${SIM:-$HOME/ahnaf/public-demos/bin/sim-main}; P=${NRF_USB_PORT:-47341}
cd "$D"
for case in ${CASES:-h3pair h16pair h3flood h40pair}; do
  hold=${case#h}; hold=${hold%%[a-z]*}; mode=${case#h$hold}
  sed "s/^HOLD = 3 .*/HOLD = $hold/" peers/ble_xbox.py > peers/ble_xbox_adv.py
  sed 's#peers/ble_xbox.py#peers/ble_xbox_adv.py#' nrf_ble_xbox.yaml > nrf_ble_xbox_adv.yaml
  for ref in main 290; do
    cp "$C/scn/elf/nrf_$ref.elf" elf/bt2usb_feather_nrf52840.elf
    "$SIM" run --scenario nrf_ble_xbox_adv.yaml --timeout 12 --ascii --usb-raw joypad.usbd:$P --output "$R/$case.$ref.console.txt" >"$R/$case.$ref.sim.log" 2>&1 &
    SP=$!; n=0; until nc -z 127.0.0.1 $P 2>/dev/null; do kill -0 $SP 2>/dev/null || break; n=$((n+1)); [ $n -gt 300 ] && break; sleep 0.2; done
    python3 xbox_rumble_adv.py $P 60 5 $mode > "$R/$case.$ref.host.txt" 2>&1; wait $SP
    grep -E "rumble write|write response" "$R/$case.$ref.sim.log" | sed 's/^\[[0-9.]*s\] *//' > "$R/$case.$ref.pad.txt"
    grep -E "send_write_report|HardFault|FATAL|fault" "$R/$case.$ref.console.txt" >> "$R/$case.$ref.pad.txt"
  done
done
rm -f peers/ble_xbox_adv.py nrf_ble_xbox_adv.yaml
