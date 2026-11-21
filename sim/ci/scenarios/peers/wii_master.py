# Wii console side of the extension port, as a bit-banged I2C master (Scripted.ScriptedGpioPeer).
# line 0 = SDA (pad GP4), line 1 = SCL (pad GP5); inputs are the sensed pad levels, outputs are driven actively
# (pyrite's RP2040 pad cannot release an external driver, so "released" = drive high; the chip's open-drain low wins).
# Protocol, from wiibrew (cited in results/226/review.md):
#   https://wiibrew.org/wiki/Wiimote/Extension_Controllers  : slave 0x52, 400 kHz; unencrypted init = write 0x55 to
#     0xA400F0 then 0x00 to 0xA400FB; ID = read 6 bytes at 0xA400FA (0000 A420 0101 = Classic Controller); data at 0xA40000.
#   https://wiibrew.org/wiki/Wiimote/Extension_Controllers/Classic_Controller : data format 0x01 (6 B) / 0x03 (8 B),
#     all buttons active low (bit layouts in decode()).
# Each register access is write(addr) + STOP, then read(n) + STOP, which is what the firmware's header documents
# for the Wiimote. Config JSON: {"fmt": 1|3, "start_ms": 1500, "poll_ms": 16.6}.
import json

BTN4 = {7: "DR", 6: "DD", 5: "LT", 4: "-", 3: "HOME", 2: "+", 1: "RT"}
BTN5 = {7: "ZL", 6: "B", 5: "Y", 4: "A", 3: "X", 2: "ZR", 1: "DL", 0: "DU"}

def decode(fmt, b):
    if fmt == 1:
        lx, ly = b[0] & 63, b[1] & 63
        rx = ((b[0] >> 3) & 0x18) | ((b[1] >> 5) & 0x06) | (b[2] >> 7)
        ry = b[2] & 31
        lt = ((b[2] >> 2) & 0x18) | (b[3] >> 5)
        rt = b[3] & 31
        b4, b5 = b[4], b[5]
        sticks = "LX=%d/63 LY=%d/63 RX=%d/31 RY=%d/31 LT=%d/31 RT=%d/31" % (lx, ly, rx, ry, lt, rt)
    else:
        sticks = "LX=%d LY=%d RX=%d RY=%d LT=%d RT=%d (0-255)" % (b[0], b[2], b[1], b[3], b[4], b[5])
        b4, b5 = b[6], b[7]
    pressed = [n for k, n in BTN4.items() if not b4 >> k & 1] + [n for k, n in BTN5.items() if not b5 >> k & 1]
    return sticks, pressed

def log(ctx, m):
    ctx.info("[wiimaster] t=%.3fs %s" % (ctx.now_us / 1e6, m))

class Slave:
    def __init__(self, ctx):
        self.ctx = ctx
        c = getattr(ctx, "config", {}) or {}
        self.fmt = int(c.get("fmt", 1)); self.start_us = int(c.get("start_ms", 1500) * 1000)
        self.poll_us = int(c.get("poll_ms", 16.6) * 1000); self.step_ns = int(c.get("step_ns", 833))
        self.sda_in = True; self.scl_in = True; self.sampled = True; self.wait = False
        self.gap_us = int(c.get('gap_us', 0)); self.last = None; self.gen = self.main()
        ctx.schedule_oneshot(self.start_us)

    def on_gpio(self, line, level):
        if line == 0: self.sda_in = bool(level)
        else: self.scl_in = bool(level)

    def on_timer(self):
        if self.wait and not self.scl_in:          # slave stretching SCL
            self.nw = getattr(self, "nw", 0) + 1
            if self.nw < 40: log(self.ctx, "SCL held low by slave (stretch) #%d" % self.nw)
            self.ctx.schedule_oneshot_ns(1000); return
        self.wait = False
        while True:
            try: a = next(self.gen)
            except StopIteration: return
            if a[0] == "s": self.sampled = self.sda_in; continue
            if a[0] == "i": self.ctx.schedule_oneshot(max(1, a[1])); return
            _, scl, sda, wait = a
            if scl: self.ctx.gpio(0).set(sda); self.ctx.gpio(1).set(scl)
            else: self.ctx.gpio(1).set(scl); self.ctx.gpio(0).set(sda)   # SCL falls before SDA moves: no false STOP
            self.wait = wait
            self.ctx.schedule_oneshot_ns(self.step_ns); return

    # ---- bit level ----
    def d(self, scl, sda, wait=False): return ("d", scl, sda, wait)

    def start(self):
        yield self.d(1, 1, True); yield self.d(1, 0); yield self.d(0, 0)

    def stop(self):
        yield self.d(0, 0); yield self.d(1, 0, True); yield self.d(1, 1)

    def wbyte(self, v):                         # -> self.acked
        for i in range(7, -1, -1):
            bit = v >> i & 1
            yield self.d(0, bit); yield self.d(1, bit, True); yield ("s",); yield self.d(0, bit)
        yield self.d(0, 1); yield self.d(1, 1, True); yield ("s",)
        self.acked = not self.sampled
        yield self.d(0, 1)

    def rbyte(self, ack):                       # -> self.rx
        v = 0
        for _ in range(8):
            yield self.d(0, 1); yield self.d(1, 1, True); yield ("s",)
            v = v << 1 | int(self.sampled); yield self.d(0, 1)
        self.rx = v
        yield self.d(0, 0 if ack else 1); yield self.d(1, 0 if ack else 1, True); yield self.d(0, 1); yield ("i", getattr(self, 'gap_us', 0) or 1)

    # ---- transactions ----
    def write(self, data):
        yield from self.start()
        ok = True
        for v in [0x52 << 1] + list(data):
            yield from self.wbyte(v); ok = ok and self.acked
        yield from self.stop(); self.ok = ok

    def read(self, n):
        yield from self.start()
        yield from self.wbyte(0x52 << 1 | 1)
        if not self.acked:
            yield from self.stop(); self.data = None; return
        out = []
        for i in range(n):
            yield from self.rbyte(i < n - 1); out.append(self.rx)
        yield from self.stop(); self.data = bytes(out)

    def regs(self, addr, n):
        yield from self.write([addr]); yield ("i", 200)
        yield from self.read(n)

    def main(self):
        ctx = self.ctx
        yield from self.write([0xF0, 0x55]); log(ctx, "write 0xF0=0x55 acked=%s" % self.ok); yield ("i", 200)
        yield from self.write([0xFB, 0x00]); log(ctx, "write 0xFB=0x00 acked=%s" % self.ok); yield ("i", 200)
        yield from self.regs(0xFA, 6); log(ctx, "ID @0xFA = %s" % (self.data.hex() if self.data else None))
        yield from self.regs(0x20, 16); log(ctx, "cal @0x20 = %s" % (self.data.hex() if self.data else None))
        if self.fmt == 3:
            yield from self.write([0xFE, 0x03]); log(ctx, "write 0xFE=0x03 acked=%s" % self.ok); yield ("i", 200)
        n = 6 if self.fmt == 1 else 8
        while True:
            t0 = ctx.now_us
            yield from self.regs(0x00, n)
            if self.data and self.data != self.last:
                self.last = self.data
                s, p = decode(self.fmt, self.data)
                log(ctx, "data %s | %s | pressed=%s" % (self.data.hex(), s, p))
            elif not self.data:
                log(ctx, "read NACK")
            yield ("i", self.poll_us - (ctx.now_us - t0))
