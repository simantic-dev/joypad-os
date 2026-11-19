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
exit $rc
