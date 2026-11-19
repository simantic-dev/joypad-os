#!/usr/bin/env python3
"""USB host for the nRF52840 bt2usb run (`sim --usb-raw joypad.usbd:<port>`): enumerate the
device, subscribe to its HID IN endpoint and log every input report with its virtual time.
usage: nrf_ble_host.py <port> <seconds_of_reports>"""
import json, sys, time
from peer import Usb

# SInput report 0x01 (src/usb/usbd/descriptors/sinput_descriptors.h): buttons u32 LE at [3:7], LX/LY i16 at [7:11]
BTN = {"EAST": 0, "SOUTH": 1, "START": 16}
u = Usb(int(sys.argv[1]))
u.enumerate()
n, last = 0, None
end = time.time() + float(sys.argv[2])      # wall-clock guard only
while time.time() < end:
    try:
        if not (chunk := u.s.recv(65536)):    # sim ended
            break
    except (ConnectionError, OSError):
        break
    u.buf += chunk
    *lines, u.buf = u.buf.split(b"\n")
    msgs = [json.loads(l) for l in lines if l.strip()]
    for m in msgs:
        if m.get("event") == "in":
            n += 1
            d = m["data"]
            b = bytes.fromhex(d)
            if b[0] != 1:
                continue
            btn, lx, ly = int.from_bytes(b[3:7], "little"), int.from_bytes(b[7:9], "little", signed=True), int.from_bytes(b[9:11], "little", signed=True)
            names = [k for k, bit in BTN.items() if btn >> bit & 1]
            state = (btn, lx, ly)
            if state != last:
                print(f"console sees t={m.get('t_us', 0) / 1e6:.3f}s buttons={'+'.join(names) or '-'} lx={lx} ly={ly}")
                last = state
print(f"{n} reports")
