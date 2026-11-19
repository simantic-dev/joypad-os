#!/bin/sh
# usage: sim/run_nrf_ble.sh   -- bt2usb on one simulated nRF52840 (Feather), a Zephyr HID-over-GATT gamepad on a
# second one (sim/peers/nrf_pad), a USB console host on the first one's USBD. Needs sim >= 0.10.5.
cd "$(dirname "$0")" || exit 1
SIM=${SIM:-sim}; OUT=${OUT:-out}; mkdir -p "$OUT"; P=${NRF_USB_PORT:-47110}
"$SIM" run --scenario nrf_ble.yaml --timeout 7 --ascii --usb-raw joypad.usbd:$P \
    --output "$OUT/nrf_ble.console.txt" >"$OUT/nrf_ble.sim.log" 2>&1 &
SIM_PID=$!; trap 'kill $SIM_PID 2>/dev/null' EXIT
n=0; until nc -z 127.0.0.1 $P 2>/dev/null; do kill -0 $SIM_PID 2>/dev/null || { cat "$OUT/nrf_ble.sim.log"; exit 1; }; n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2; done
python3 nrf_ble_host.py $P 60 | tee "$OUT/nrf_ble.peer.txt"; wait $SIM_PID
