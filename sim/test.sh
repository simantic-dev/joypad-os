#!/bin/sh
# Runs the usb2usb remapper image (sim/elf/a_ps5default_*.elf) on the simulated RP2040 for 8 virtual seconds
# with sim/run.sh refresh: a scripted USB console host, dongle and gamepad play around it.
# Pass = the firmware enumerates as a HID gamepad, the gamepad's HOME presses reach the console
# (DOWN then UP after the 192 ms hold), the console's sign requests are answered, no fault lines.
cd "$(dirname "$0")/.." || exit 1
OUT=$(mktemp -d); trap 'rm -rf "$OUT"' EXIT
rc=0
SIM=${SIM:-sim} OUT=$OUT sh sim/run.sh refresh >"$OUT/peer.txt" 2>&1
chk() { if grep -qF -- "$2" "$OUT/peer.txt"; then echo "ok   $1"; else echo "FAIL $1"; rc=1; fi; }
chk "enumerates as 2b81:0101" "usb device 2b81:0101"
chk "HID IN endpoint configured" "HID IN endpoint 0x81"
chk "console sees HOME DOWN" "console sees HOME DOWN"
chk "console sees HOME UP after 192 ms hold" "HOME UP   (held 192 ms)"
chk "11 reports, 12 sign requests" "11 reports to console, 12 sign requests"
if grep -qiE 'panic|hardfault|guru' "$OUT/refresh.console.txt" "$OUT/refresh.sim.log"; then echo "FAIL no fault"; rc=1; else echo "ok   no fault"; fi

# nRF52840: bt2usb (Feather build, NCS 3.1.0) on one machine, a Python ScriptedBlePeer HID-over-GATT gamepad (sim/peers/ble_pad.py)
# on the BLE medium. Pass = LESC pairing + HOGP discovery, USB enumeration, and the pad's A, B+START and
# left-stick moves arrive at the USB console host as SInput reports.
SIM=${SIM:-sim} OUT=$OUT sh sim/run_nrf_ble.sh >"$OUT/nrf_ble.txt" 2>&1
chk2() { if grep -qF -- "$2" "$3"; then echo "ok   $1"; else echo "FAIL $1"; rc=1; fi; }
chk2 "nRF: enumerates as 2e8a:10c6" "usb device 2e8a:10c6" "$OUT/nrf_ble.txt"
chk2 "nRF: BLE pairing succeeds" "SM: Pairing successful" "$OUT/nrf_ble.console.txt"
chk2 "nRF: HID reports enabled" "Ready to receive HID reports" "$OUT/nrf_ble.console.txt"
chk2 "nRF: console sees A" "buttons=SOUTH lx=0 ly=0" "$OUT/nrf_ble.txt"
chk2 "nRF: console sees B+START" "buttons=EAST+START" "$OUT/nrf_ble.txt"
chk2 "nRF: console sees left stick right/up" "lx=32512 ly=-32768" "$OUT/nrf_ble.txt"
# Full pad: every input once. HID usage 16 has no slot in Joypad's generic button map (usages 1..15 only), so 15 buttons.
for b in SOUTH EAST WEST NORTH L1 R1 L2 R2 BACK START L3 R3 GUIDE CAPTURE BIT25; do chk2 "nRF: button $b seen alone" "seen button $b" "$OUT/nrf_ble.txt"; done
for h in U UR R DR D DL L UL; do chk2 "nRF: hat $h" "seen hat $h" "$OUT/nrf_ble.txt"; done
for a in lx ly rx ry; do for e in low high; do chk2 "nRF: stick $a $e extreme" "seen stick $a $e" "$OUT/nrf_ble.txt"; done; done
for t in lt rt; do chk2 "nRF: trigger $t 0 -> full" "seen trigger $t" "$OUT/nrf_ble.txt"; done
# Output reports (rumble / LED) are reported, never required.
grep -h "output report write" "$OUT/nrf_ble.sim.log" || echo "info nRF: Joypad wrote no output report (rumble/LED) to the pad"
if grep -qiE 'panic|hardfault|assert|fatal' "$OUT/nrf_ble.console.txt" "$OUT/nrf_ble.sim.log"; then echo "FAIL nRF: no fault"; rc=1; else echo "ok   nRF: no fault"; fi
exit $rc
