#!/usr/bin/env python3
"""Reads the RP2040 remapper-B uart1 link (SLIP frames from src/uart_peer/uart_peer.h) and prints what B ships to A.
usage: host_peer.py <uart_port> <seconds_of_B_time>   (stops after that many DEBUG/uptime ms or on close)"""
import socket, struct, sys, zlib, time
END, ESC, ESC_END, ESC_ESC = 0xC0, 0xDB, 0xDC, 0xDD
def frame(mtype, payload=b""):
    body = bytes([mtype]) + payload; body += struct.pack("<I", zlib.crc32(body)); out = bytearray()
    for b in body: out += bytes([ESC, ESC_END]) if b == END else bytes([ESC, ESC_ESC]) if b == ESC else bytes([b])
    return bytes(out) + bytes([END])
def main():
    s = socket.create_connection(("127.0.0.1", int(sys.argv[1]))); s.settimeout(40)
    rx, esc, t0 = bytearray(), False, time.time()
    while True:
        try: d = s.recv(65536)
        except socket.timeout: break
        if not d: break
        for b in d:
            if b == END:
                f = bytes(rx); rx, esc = bytearray(), False
                if len(f) < 5 or zlib.crc32(f[:-4]) != struct.unpack("<I", f[-4:])[0]: continue
                t, p = f[0], f[1:-4]
                if t == 1:
                    pl, ty, bt = struct.unpack_from("<BBI", p); an = list(p[6:12])
                    print(f"EVENT player={pl} type={ty} buttons={bt:#07x} analog(lx,ly,rx,ry,l2,r2)={an}", flush=True)
                elif t == 0x0A:
                    pl, fl, ta = struct.unpack_from("<BBB", p); tx = struct.unpack_from("<2H", p, 3); ty_ = struct.unpack_from("<2H", p, 7)
                    print(f"EXT player={pl} flags={fl:#x} touch_active={ta:#x} touch_x={list(tx)} touch_y={list(ty_)} accel={list(struct.unpack_from('<3h', p, 11))} gyro={list(struct.unpack_from('<3h', p, 17))}", flush=True)
                elif t == 3:
                    m, dc, vid, pid, up = struct.unpack_from("<BBHHI", p)
                    print(f"DEBUG dev_count={dc} last={vid:04x}:{pid:04x} uptime_ms={up}", flush=True)
                    if up > float(sys.argv[2]) * 1000: return
            elif esc: rx.append(END if b == ESC_END else ESC if b == ESC_ESC else b); esc = False
            elif b == ESC: esc = True
            else: rx.append(b)
main()
