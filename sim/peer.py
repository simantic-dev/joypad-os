#!/usr/bin/env python3
"""Everything around joypad-os remapper A, for a pyrite run:
  * the console: a USB host on `sim --usb-raw usb:<port>` that enumerates A and
    logs every HID input report;
  * B + the P5General dongle + the pad: the uart_peer link on
    `sim --uart-tcp uart1:<port>` (frame format from src/uart_peer/uart_peer.h).

Clock: A sends a STATUS frame every 8 ms of ITS time, so the script counts those
("ticks") instead of trusting wall-clock.

usage: peer.py <usb_port> <uart_port> <change|refresh|stream> [sign_delay_ticks]
  change   pad sends an EVENT only when a button changes
  refresh  change + B's 100 ms state re-send (joypad-os 2145ffa)
  stream   pad sends an EVENT every tick (a wired pad that reports continuously)
"""
import json, select, socket, struct, sys, zlib

END, ESC, ESC_END, ESC_ESC = 0xC0, 0xDB, 0xDC, 0xDD
MSG_EVENT, MSG_STATUS, SIGN_REQ, SIGN_RESP, DONGLE = 0x01, 0x02, 0x04, 0x05, 0x09
HOME = 1 << 16          # JP_BUTTON_A1
TAP_TICKS = 5           # 40 ms
TAPS_AT = (125, 250, 375)
END_TICK = 500


def frame(mtype, payload=b""):
    body = bytes([mtype]) + payload
    body += struct.pack("<I", zlib.crc32(body))
    out = bytearray()
    for b in body:
        out += bytes([ESC, ESC_END]) if b == END else bytes([ESC, ESC_ESC]) if b == ESC else bytes([b])
    return bytes(out) + bytes([END])


def event(buttons):     # uart_peer_event_t: player, type=GAMEPAD, buttons, 6 analog
    return frame(MSG_EVENT, struct.pack("<BBI6B", 0, 1, buttons, 128, 128, 128, 128, 0, 0))


class Usb:
    def __init__(self, port):
        self.s = socket.create_connection(("127.0.0.1", port))
        self.buf, self.events, self.n = b"", [], 0

    def pump(self):
        self.buf += self.s.recv(65536)
        *lines, self.buf = self.buf.split(b"\n")
        return [json.loads(l) for l in lines if l.strip()]

    def req(self, **kw):
        self.n += 1
        kw["id"] = self.n
        self.s.sendall(json.dumps(kw).encode() + b"\n")
        while True:
            for m in self.pump():
                if m.get("id") == self.n:
                    return m
                self.events.append(m)

    def setup(self, rt, rq, val=0, idx=0, length=0):
        r = self.req(op="setup", bmRequestType=rt, bRequest=rq, wValue=val, wIndex=idx, wLength=length)
        if not r.get("ok"):
            sys.exit(f"control {rt:#x}/{rq:#x}/{val:#x} failed: {r}")
        return bytes.fromhex(r.get("data", ""))

    def enumerate(self):
        print("usb reset:", self.req(op="reset"))
        dev = self.setup(0x80, 6, 0x0100, 0, 18)
        print(f"usb device {dev[8] | dev[9] << 8:04x}:{dev[10] | dev[11] << 8:04x}")
        self.setup(0x00, 5, 1)                                  # SET_ADDRESS
        total = struct.unpack_from("<H", self.setup(0x80, 6, 0x0200, 0, 9), 2)[0]
        cfg, ep_in, i = self.setup(0x80, 6, 0x0200, 0, total), None, 0
        while i < len(cfg):
            if cfg[i + 1] == 5 and cfg[i + 2] & 0x80 and cfg[i + 3] & 3 == 3 and ep_in is None:
                ep_in = cfg[i + 2]
            i += cfg[i]
        self.setup(0x00, 9, cfg[5])                             # SET_CONFIGURATION
        print(f"usb configured, HID IN endpoint {ep_in:#x}")
        print("subscribe:", self.req(op="subscribe", ep=ep_in))


LOG = []


def main():
    usb_port, uart_port, mode = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    sign_delay = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    link = socket.create_connection(("127.0.0.1", uart_port))
    usb = Usb(usb_port)
    usb.enumerate()

    tick, rx, esc = 0, bytearray(), False
    buttons, last_sent_tick, home, home_down_tick = 0, 0, None, 0
    sign_q, n_reports, n_sign = [], 0, 0

    def on_report(data):
        nonlocal home, home_down_tick, n_reports
        n_reports += 1
        LOG.append((8 * tick, data.hex()))
        h = data[10] & 1
        if h != home:
            held = f"   (held {8 * (tick - home_down_tick)} ms)" if home == 1 and not h else ""
            print(f"  t={8 * tick:5d} ms  console sees HOME {'DOWN' if h else 'UP'}{held}")
            if h:
                home_down_tick = tick
            home = h

    def on_tick():
        nonlocal buttons, last_sent_tick
        if tick % 30 == 1:
            link.sendall(frame(DONGLE, b"\x01"))
        want = HOME if any(t <= tick < t + TAP_TICKS for t in TAPS_AT) else 0
        if want != buttons:
            buttons = want
            print(f"  t={8 * tick:5d} ms  pad: HOME {'press' if want else 'release'}")
            link.sendall(event(buttons)); last_sent_tick = tick
        elif mode == "stream" or (mode == "refresh" and tick - last_sent_tick >= 12):
            link.sendall(event(buttons)); last_sent_tick = tick
        while sign_q and sign_q[0][0] <= tick:
            link.sendall(frame(SIGN_RESP, sign_q.pop(0)[1]))

    def on_frame(f):
        nonlocal tick, n_sign
        if len(f) < 5 or zlib.crc32(bytes(f[:-4])) != struct.unpack("<I", bytes(f[-4:]))[0]:
            return
        if f[0] == MSG_STATUS:
            tick += 1
            on_tick()
        elif f[0] == SIGN_REQ:
            n_sign += 1
            if sign_delay:
                sign_q.append((tick + sign_delay, bytes(f[1:-4])))
            else:
                link.sendall(frame(SIGN_RESP, bytes(f[1:-4])))

    for m in usb.events:
        if m.get("event") == "in":
            on_report(bytes.fromhex(m["data"]))
    while tick < END_TICK:
        for s in select.select([link, usb.s], [], [], 30)[0] or sys.exit("no traffic for 30 s"):
            if s is usb.s:
                for m in usb.pump():
                    if m.get("event") == "in":
                        on_report(bytes.fromhex(m["data"]))
                continue
            for b in link.recv(65536) or sys.exit("link closed"):
                if b == END:
                    if rx:
                        on_frame(rx)
                    rx, esc = bytearray(), False
                elif esc:
                    rx.append(END if b == ESC_END else ESC if b == ESC_ESC else b); esc = False
                elif b == ESC:
                    esc = True
                else:
                    rx.append(b)
    if home == 1:
        print(f"  t={8 * tick:5d} ms  HOME STILL DOWN at end of run")
    import os
    open(os.environ.get("REPORT_LOG", "reports.csv"), "w").write("t_ms,report_hex\n" + "".join(f"{t},{h}\n" for t, h in LOG))
    print(f"  {n_reports} reports to console, {n_sign} sign requests")


if __name__ == "__main__":
    main()
