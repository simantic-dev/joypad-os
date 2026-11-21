#!/usr/bin/env python3
"""USB host with CDC ACM for Joypad's text-mode console (`--usb-raw <periph>:<port>`).
usage: cdc_host.py <port> <wait_virtual_s> <command-json> [<command-json> ...]
Enumerates, sets DTR, then sends each command line (waits up to 1.5 s wall for a reply) and prints the replies."""
import json, struct, sys, time

def crc16(b):
    c = 0xFFFF
    for x in b:
        c ^= x << 8
        for _ in range(8): c = ((c << 1) ^ 0x1021 if c & 0x8000 else c << 1) & 0xFFFF
    return c

def cframe(seq, js):  # [AA][len16][type=1 CMD][seq][json][crc16 over type+seq+json]
    body = bytes([1, seq]) + js.encode()
    return b"\xaa" + struct.pack("<H", len(js)) + body + struct.pack("<H", crc16(body))

def parse(buf):  # -> list of (type, payload) frames in buf
    out = []
    while (i := buf.find(b"\xaa")) >= 0 and len(buf) >= i + 5:
        n = buf[i + 1] | buf[i + 2] << 8
        if len(buf) < i + 5 + n + 2: break
        out.append((buf[i + 3], buf[i + 5:i + 5 + n])); buf = buf[i + 5 + n + 2:]
    return out
from peer import Usb

u = Usb(int(sys.argv[1])); wait_us = int(float(sys.argv[2]) * 1e6)
print("usb reset:", u.req(op="reset"))
dev = u.setup(0x80, 6, 0x0100, 0, 18)
print(f"usb device {dev[8] | dev[9] << 8:04x}:{dev[10] | dev[11] << 8:04x}")
u.setup(0x00, 5, 1)
total = struct.unpack_from("<H", u.setup(0x80, 6, 0x0200, 0, 9), 2)[0]
cfg, i, eps, cls, comm = u.setup(0x80, 6, 0x0200, 0, total), 0, {}, None, 0
while i < len(cfg):
    if cfg[i + 1] == 4:
        cls = cfg[i + 5]
        if cls == 2: comm = cfg[i + 2]
    if cfg[i + 1] == 5 and cfg[i + 3] & 3 == 2 and cls == 0x0A: eps['in' if cfg[i + 2] & 0x80 else 'out'] = cfg[i + 2]
    i += cfg[i]
u.setup(0x00, 9, cfg[5])
u.req(op="setup", bmRequestType=0x21, bRequest=0x22, wValue=3, wIndex=comm, wLength=0)  # SET_CONTROL_LINE_STATE DTR|RTS
print("cdc endpoints:", eps)
u.req(op="subscribe", ep=eps['in'])
while u.req(op="setup", bmRequestType=0x80, bRequest=0, wValue=0, wIndex=0, wLength=2).get("t_us", 0) < wait_us: pass
for seq, cmd in enumerate(sys.argv[3:], 1):
    if cmd.startswith('wait:'):  # wait:<virtual seconds since boot>
        u.s.settimeout(None)
        while u.req(op="setup", bmRequestType=0x80, bRequest=0, wValue=0, wIndex=0, wLength=2).get("t_us", 0) < float(cmd[5:]) * 1e6: pass
        continue
    u.s.settimeout(None)
    r = u.req(op="out", ep=eps['out'], data=cframe(seq, cmd).hex())
    print(f"host> {cmd}  (t={r.get('t_us', 0) / 1e6:.3f}s ok={r.get('ok')})")
    got, end = b"", time.time() + 1.5
    while time.time() < end and not any(t == 2 for t, _ in parse(got)):
        try:
            u.s.settimeout(0.3); u.buf += u.s.recv(65536)
        except OSError: pass
        *lines, u.buf = u.buf.split(b"\n")
        for l in lines:
            if l.strip():
                m = json.loads(l)
                if m.get("event") == "in": got += bytes.fromhex(m["data"])
                else: u.events.append(m)
    rsp = [p.decode(errors="replace") for t, p in parse(got) if t == 2]
    print("dev< " + (rsp[0] if rsp else "(no reply)"))
