#!/usr/bin/env python3
"""USB host for #290: wait for the first BLE pad input report (pad paired and mapped), send an SInput haptic START,
wait ~20 virtual ms (virtual clock = t_us in replies), then haptic STOP while the first BLE write is still unacked.
usage: xbox_rumble_host.py <port> <wall_seconds>"""
import json, sys, time
from peer import Usb

def haptic(u, amp):  # SET_REPORT output id 3: [CMD_HAPTIC=1, type=2, L amp, L brake, R amp, R brake]
    r = u.req(op="setup", bmRequestType=0x21, bRequest=9, wValue=0x0300 | 3, wIndex=0, wLength=6,
              data=bytes([1, 2, amp, 0, amp, 0]).hex())
    print(f"host: haptic amp={amp} t={r.get('t_us', 0) / 1e3:.1f} ms ok={r.get('ok')}")
    return r.get("t_us", 0)

u = Usb(int(sys.argv[1])); u.enumerate()
end, got, t_in = time.time() + float(sys.argv[2]), 0, None
while time.time() < end and got < 3:
    try:
        u.buf += u.s.recv(65536)
    except OSError:
        break
    *lines, u.buf = u.buf.split(b"\n")
    got += sum(1 for l in lines if l.strip() and json.loads(l).get("event") == "in")
print("host: pad reports arriving; waiting for DIS PnP (VID 045E) to be applied")
while u.req(op="setup", bmRequestType=0x80, bRequest=0, wValue=0, wIndex=0, wLength=2).get("t_us", 0) < 3_500_000: pass
t0 = haptic(u, 255)
while True:   # virtual clock: GET_STATUS replies carry t_us
    t = u.req(op="setup", bmRequestType=0x80, bRequest=0, wValue=0, wIndex=0, wLength=2).get("t_us", 0)
    if t - t0 >= 20_000 or time.time() > end: break
haptic(u, 0)
time.sleep(float(sys.argv[3]) if len(sys.argv) > 3 else 6)
