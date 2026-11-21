#!/usr/bin/env python3
"""#290 adversarial USB host (extends xbox_rumble_host.py): after the BLE pad is mapped, send SInput haptic START/STOP sequences.
usage: xbox_rumble_adv.py <port> <wall_s> <tail_s> <mode>   mode = pair (START, STOP 20 ms later) | flood (10x START/STOP 20 ms apart, last is STOP)"""
import json, sys, time
from peer import Usb
def haptic(u, amp):
    r = u.req(op="setup", bmRequestType=0x21, bRequest=9, wValue=0x0300 | 3, wIndex=0, wLength=6, data=bytes([1, 2, amp, 0, amp, 0]).hex())
    print(f"host: haptic amp={amp} t={r.get('t_us', 0) / 1e3:.1f} ms"); return r.get("t_us", 0)
def now(u): return u.req(op="setup", bmRequestType=0x80, bRequest=0, wValue=0, wIndex=0, wLength=2).get("t_us", 0)
def wait(u, us):
    t0 = now(u)
    while now(u) - t0 < us: pass
u = Usb(int(sys.argv[1])); u.enumerate()
end, got = time.time() + float(sys.argv[2]), 0
while time.time() < end and got < 3:
    try: u.buf += u.s.recv(65536)
    except OSError: break
    *lines, u.buf = u.buf.split(b"\n"); got += sum(1 for l in lines if l.strip() and json.loads(l).get("event") == "in")
while now(u) < 3_500_000: pass
if sys.argv[4] == "pair":
    haptic(u, 255); wait(u, 20_000); haptic(u, 0)
else:
    for i in range(10):
        haptic(u, 255); wait(u, 20_000); haptic(u, 0); wait(u, 20_000)
time.sleep(float(sys.argv[3]))
