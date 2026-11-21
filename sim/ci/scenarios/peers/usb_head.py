# Common half of the scripted USB device on the RP2040 native host port (USB.ScriptedUsbDevice, pyrite).
# run_host.sh prepends VID/PID/KIND and appends a kind file (usb_<kind>.py) that defines
# REPORT_DESC, CONFIG_BODY (interface+endpoints), DEVICE_CLASS and phases(n) -> bytes|None.
import sys

def log(*a):
    print("[usbpeer]", *a, file=sys.stderr, flush=True)

def le16(v):
    return bytes([v & 255, v >> 8])

def device_desc(vid, pid, dclass=0):
    return bytes([18, 1, 0x00, 0x02, dclass, 0, 0, 64]) + le16(vid) + le16(pid) + bytes([0x00, 0x01, 0, 0, 0, 1])

def config_desc(body):
    return bytes([9, 2]) + le16(9 + len(body)) + bytes([len(IFACES), 1, 0, 0x80, 50]) + body

def string_desc(i):
    if i == 0: return bytes([4, 3, 0x09, 0x04])                                 # LANGID 0x0409
    s = {1: globals().get("MANUFACTURER"), 2: globals().get("PRODUCT")}.get(i)
    if s is None: return STALL
    b = s.encode("utf-16-le")
    return bytes([2 + len(b), 3]) + b

def hid_desc(rlen):
    return bytes([9, 0x21, 0x11, 0x01, 0, 1, 0x22]) + le16(rlen)

class Base:
    def __init__(self):
        self.polls = {}
        self.dev = device_desc(VID, PID, DEVICE_CLASS)
        self.cfg = globals().get("CONFIG_FULL") or config_desc(CONFIG_BODY)   # CONFIG_FULL: a published dump, verbatim
        if globals().get("MANUFACTURER"):                                       # strings 1/2 as the real device reports them
            self.dev = self.dev[:14] + bytes([1, 2, 0]) + self.dev[17:]
        log("device", hex(VID), hex(PID), "config bytes", len(self.cfg))

    def on_setup(self, setup, data):
        rt, rq = setup[0], setup[1]
        val = setup[2] | setup[3] << 8
        idx = setup[4] | setup[5] << 8
        ln = setup[6] | setup[7] << 8
        if rq == 6 and rt in (0x80, 0x81):                      # GET_DESCRIPTOR
            t = val >> 8
            if t == 1: return self.dev
            if t == 2: return self.cfg[:ln] if ln else self.cfg
            if t == 3: return string_desc(val & 255)
            if t == 0x22: return REPORT_DESC
            return STALL
        if rt == 0x00 and rq in (5, 9): return b""               # SET_ADDRESS / SET_CONFIGURATION
        if rt == 0x21 and rq in (0x0a, 0x0b): return b""         # SET_IDLE / SET_PROTOCOL
        if rt == 0x21 and rq == 9:                               # HID SET_REPORT
            log("SET_REPORT type", val >> 8, "id", val & 255, "data", bytes(data).hex())
            return b""
        if rt == 0xa1 and rq == 1:                               # HID GET_REPORT
            r = GET_REPORT_REPLY.get((val >> 8, val & 255), STALL) if GET_REPORT_REPLY is not None else STALL
            log("GET_REPORT type", val >> 8, "id", val & 255, "len", ln, "-> %d bytes" % len(r) if isinstance(r, (bytes, bytearray)) else "-> STALL")
            got_report(val & 255)
            return r
        log("control", "rt=%02x rq=%02x val=%04x idx=%04x len=%d" % (rt, rq, val, idx, ln), "-> STALL")
        return STALL

    def on_in(self, ep):
        n = self.polls[ep] = self.polls.get(ep, 0) + 1
        r = phases(ep, n)
        return NAK if r is None else r

    def on_out(self, ep, data):
        log("OUT ep", ep, bytes(data).hex())
        return ACK

GET_REPORT_REPLY = None

def got_report(i):
    pass
