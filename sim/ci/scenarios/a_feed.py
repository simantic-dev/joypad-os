#!/usr/bin/env python3
"""Feeds remapper A over the uart_peer link (the USB side is read by `--usb-hid-tap usb`, not by this script).
usage: a_feed.py <uart_port> ; A's STATUS frame (every 8 ms of A time) is the clock; EVENT every tick.
Timeline (ticks of 8 ms): 0-60 neutral, 60-120 B1 (Cross), 120-180 left stick up-right, 180-240 right stick down-left, 240-300 B1+L2 full."""
import socket, struct, sys, zlib, importlib.util, os
spec = importlib.util.spec_from_file_location("jp_peer", os.path.join(os.environ["JP_SIM_DIR"], "peer.py"))
jp = importlib.util.module_from_spec(spec); spec.loader.exec_module(jp)
B1, L2 = 1 << 0, 1 << 6
def f(t):
    if t < 60: return 0, 128, 128, 128, 128, 0, 0
    if t < 120: return B1, 128, 128, 128, 128, 0, 0
    if t < 180: return 0, 255, 0, 128, 128, 0, 0
    if t < 240: return 0, 128, 128, 0, 255, 0, 0
    return B1, 128, 128, 128, 128, 255, 0
link = socket.create_connection(("127.0.0.1", int(sys.argv[1]))); tick, rx, esc = 0, bytearray(), False
def on_frame(fr):
    global tick
    if len(fr) < 5 or zlib.crc32(bytes(fr[:-4])) != struct.unpack("<I", bytes(fr[-4:]))[0]: return
    if fr[0] == jp.MSG_STATUS:
        tick += 1
        b, lx, ly, rx_, ry, l2, r2 = f(tick - 270)   # the tap attaches at ~2.0 s of A time (250 ticks)
        link.sendall(jp.frame(jp.MSG_EVENT, struct.pack("<BBI6B", 0, 1, b, lx, ly, rx_, ry, l2, r2)))
while tick < 270 + 330:
    d = link.recv(65536)
    if not d: break
    for b in d:
        if b == jp.END:
            if rx: on_frame(rx)
            rx, esc = bytearray(), False
        elif esc: rx.append(jp.END if b == jp.ESC_END else jp.ESC if b == jp.ESC_ESC else b); esc = False
        elif b == jp.ESC: esc = True
        else: rx.append(b)
