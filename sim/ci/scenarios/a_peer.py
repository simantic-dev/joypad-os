#!/usr/bin/env python3
"""Drives remapper A (USB device side) over the uart_peer link and decodes what the USB console host receives.
usage: a_peer.py <usb_port> <uart_port> <ps3|switch> <sticks|capture|autofire>
A's STATUS frame comes every 8 ms of A time and is the clock (tick = 8 ms). Events are sent every tick."""
import select, socket, struct, sys, zlib, importlib.util, os
spec = importlib.util.spec_from_file_location("jp_peer", os.path.join(os.environ["JP_SIM_DIR"], "peer.py"))
jp = importlib.util.module_from_spec(spec); spec.loader.exec_module(jp)

S1, S2, B1, B3, A1 = 1 << 8, 1 << 9, 1 << 0, 1 << 2, 1 << 16
SWITCH_BITS = {0: "Y", 1: "B", 2: "A", 3: "X", 4: "L", 5: "R", 6: "ZL", 7: "ZR", 8: "MINUS", 9: "PLUS", 10: "L3", 11: "R3", 12: "HOME", 13: "CAPTURE"}

def timeline(name):
    """-> (end_tick, f(tick) -> (buttons, lx, ly, rx, ry))"""
    N = (128, 128, 128, 128)
    if name == "sticks":      # full diagonal, full cardinal, half diagonal (axes in 0..255, 128 = centre)
        pts = [N, (218, 38, 128, 128), (255, 128, 128, 128), (128, 128, 38, 218), (192, 64, 128, 128)]
        return 60 * len(pts), lambda t: (0,) + pts[min(t // 60, len(pts) - 1)]
    if name == "capture":     # SELECT alone, START alone, SELECT+START, release
        seq = [0, S1, 0, S2, 0, S1 | S2, 0]
        return 40 * len(seq), lambda t: (seq[min(t // 40, len(seq) - 1)],) + N
    if name == "autofire":    # S1+B3 held 2.1 s -> rapid-fire set; tap B1 to cycle its rate; tap S1 to exit; hold B1 1 s
        def f(t):
            if 10 <= t < 285: b = S1 | B3
            elif 500 <= t < 506: b = B1                 # tap: B1 -> 30 Hz (after the mode-entry LED indication has finished)
            elif 560 <= t < 566: b = S1                 # exit
            elif 620 <= t < 750: b = B1                 # the held button
            else: b = 0
            return (b,) + N
        return 780, f

def decode(mode, d):
    if mode == "switch" and len(d) >= 8:
        b = d[0] | d[1] << 8
        names = "+".join(n for i, n in SWITCH_BITS.items() if b >> i & 1) or "-"
        return f"buttons={b:#06x} [{names}] hat={d[2]} L=({d[3]},{d[4]}) R=({d[5]},{d[6]})"
    if mode == "ps3" and len(d) >= 10:
        return f"id={d[0]} buttons={d[2]:02x}{d[3]:02x}{d[4]:02x} L=({d[6]},{d[7]}) R=({d[8]},{d[9]})"
    return d.hex()

def main():
    usb_port, uart_port, mode, scen = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
    end, f = timeline(scen)
    link = socket.create_connection(("127.0.0.1", uart_port)); usb = jp.Usb(usb_port); usb.enumerate()
    tick, rx, esc, last, n = 0, bytearray(), False, None, 0
    def on_report(data):
        nonlocal last, n
        n += 1
        if data != last:
            print(f"  t={8 * tick:5d} ms  {decode(mode, data)}", flush=True); last = data
    def on_frame(fr):
        nonlocal tick
        if len(fr) < 5 or zlib.crc32(bytes(fr[:-4])) != struct.unpack("<I", bytes(fr[-4:]))[0]: return
        if fr[0] == jp.MSG_STATUS:
            tick += 1
            b, lx, ly, rx_, ry = f(tick)
            link.sendall(jp.frame(jp.MSG_EVENT, struct.pack("<BBI6B", 0, 1, b, lx, ly, rx_, ry, 0, 0)))
    for m in usb.events:
        if m.get("event") == "in": on_report(bytes.fromhex(m["data"]))
    while tick < end:
        for s in select.select([link, usb.s], [], [], 30)[0] or sys.exit("no traffic for 30 s"):
            if s is usb.s:
                for m in usb.pump():
                    if m.get("event") == "in": on_report(bytes.fromhex(m["data"]))
                continue
            for b in link.recv(65536) or sys.exit("link closed"):
                if b == jp.END:
                    if rx: on_frame(rx)
                    rx, esc = bytearray(), False
                elif esc: rx.append(jp.END if b == jp.ESC_END else jp.ESC if b == jp.ESC_ESC else b); esc = False
                elif b == jp.ESC: esc = True
                else: rx.append(b)
    print(f"  {n} reports")
main()
