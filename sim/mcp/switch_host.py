#!/usr/bin/env python3
"""USB console host for Joypad's Switch output (HORI-style 8-byte report): prints every button change with sim time.
usage: switch_host.py <usb_port> <seconds>"""
import json, sys, time
sys.path.insert(0, __import__("os").path.dirname(__file__) + "/.."); from peer import Usb
NAMES = ["Y", "B", "A", "X", "L", "R", "ZL", "ZR", "MINUS", "PLUS", "L3", "R3", "HOME", "CAPTURE"]
HAT = ["DU", "DU+DR", "DR", "DD+DR", "DD", "DD+DL", "DL", "DU+DL"]
u = Usb(int(sys.argv[1])); u.enumerate(); last = None; end = time.time() + float(sys.argv[2])
print("console: enumerated", flush=True)
while time.time() < end:
    try:
        chunk = u.s.recv(65536)
    except OSError:
        break
    if not chunk:
        break
    u.buf += chunk
    *lines, u.buf = u.buf.split(b"\n")
    for l in lines:
        m = json.loads(l) if l.strip() else {}
        if m.get("event") != "in" or len(b := bytes.fromhex(m["data"])) < 7:
            continue
        btn, hat, sticks = int.from_bytes(b[0:2], "little"), b[2], tuple(b[3:7])
        if (btn, hat, sticks) != last:
            names = [n for i, n in enumerate(NAMES) if btn >> i & 1] + ([HAT[hat]] if hat < 8 else [])
            print(f"console sees t={m.get('t_us', 0) / 1e6:.3f}s buttons={'+'.join(names) or '-'} lx,ly,rx,ry={sticks}", flush=True)
            last = (btn, hat, sticks)
