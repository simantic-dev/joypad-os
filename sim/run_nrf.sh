#!/bin/sh
# usage: sim/run_nrf.sh   -- usb2usb on nRF52840 (sim 0.10.0 marks the model `incomplete`)
cd "$(dirname "$0")" || exit 1
SIM=${SIM:-sim}; OUT=${OUT:-out}; mkdir -p "$OUT"; P=47103
"$SIM" NRF52840QIAA run --elf elf/usb2usb_nrf52840dk.elf --timeout 3 --ascii \
    --usb-raw usbd:$P --usb-capture "usbd:$OUT/nrf.pcap" --output "$OUT/nrf.console.txt" >"$OUT/nrf.sim.log" 2>&1 &
SIM_PID=$!; trap 'kill $SIM_PID 2>/dev/null' EXIT
n=0; until nc -z 127.0.0.1 $P 2>/dev/null; do kill -0 $SIM_PID 2>/dev/null || { cat "$OUT/nrf.sim.log"; exit 1; }; n=$((n+1)); [ $n -gt 300 ] && exit 1; sleep 0.2; done
python3 nrf_enum.py $P | tee "$OUT/nrf.enum.txt"; wait $SIM_PID
