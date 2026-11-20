#!/usr/bin/env python3
"""USB host for the nRF52840 bt2usb run (`sim --usb-raw joypad.usbd:<port>`): enumerate the
device, subscribe to its HID IN endpoint and log every input report with its virtual time.
usage: nrf_ble_host.py <port> <seconds_of_reports>"""
import json, sys, time
from peer import Usb

# SInput report 0x01 (src/usb/usbd/descriptors/sinput_descriptors.h): buttons u32 LE at [3:7], LX/LY i16 at [7:11]
BTN = {"EAST": 0, "SOUTH": 1, "NORTH": 2, "WEST": 3, "DU": 4, "DD": 5, "DL": 6, "DR": 7, "L3": 8, "R3": 9, "L1": 10, "R1": 11,
       "L2": 12, "R2": 13, "START": 16, "BACK": 17, "GUIDE": 18, "CAPTURE": 19}
# rx/ry at [11:15], lt/rt at [15:19] (i16, triggers 0..32767)
HAT = {"U": (4,), "UR": (4, 7), "R": (7,), "DR": (5, 7), "D": (5,), "DL": (5, 6), "L": (6,), "UL": (4, 6)}
seen_btn, seen_hat, lo, hi = set(), set(), {}, {}
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
            btn = int.from_bytes(b[3:7], "little")
            ax = dict(zip(("lx", "ly", "rx", "ry", "lt", "rt"), (int.from_bytes(b[o:o + 2], "little", signed=True) for o in range(7, 19, 2))))
            names = [k for k, bit in BTN.items() if btn >> bit & 1]
            dp = tuple(sorted(bit for bit in (4, 5, 6, 7) if btn >> bit & 1))
            if len(names) == 1 and not dp:
                seen_btn.add(names[0])
            seen_btn.update(f"BIT{i}" for i in range(32) if btn >> i & 1 and i not in BTN.values())
            seen_hat.update(h for h, bits in HAT.items() if dp == tuple(sorted(bits)))
            for k, v in ax.items():
                lo[k], hi[k] = min(lo.get(k, v), v), max(hi.get(k, v), v)
            state = (btn, *ax.values())
            if state != last:
                print(f"console sees t={m.get('t_us', 0) / 1e6:.3f}s buttons={'+'.join(names) or '-'} lx={ax['lx']} ly={ax['ly']} "
                      f"rx={ax['rx']} ry={ax['ry']} lt={ax['lt']} rt={ax['rt']}")
                last = state
print(f"{n} reports")
for k in sorted(seen_btn):
    print("seen button", k)
for h in sorted(seen_hat):
    print("seen hat", h)
for k in lo:
    print(f"axis {k} min={lo[k]} max={hi[k]}")
    if k in ("lt", "rt"):
        print(f"seen trigger {k}" if hi[k] >= 32000 and lo[k] == 0 else f"missing trigger {k}")
    else:
        print(f"seen stick {k} low" if lo[k] <= -32000 else f"missing stick {k} low")
        print(f"seen stick {k} high" if hi[k] >= 32000 else f"missing stick {k} high")
