# Switch 2 Pro Controller: HID interface 0 (report 0x09) + vendor interface 1 with bulk OUT 0x02 / IN 0x82, then
# filler alt-settings so the configuration descriptor is longer than the driver's 256-byte buffer (#286).
# OPT: none = every bulk command succeeds; once = bulk command #3 STALLs once; always = from command #3 on every one STALLs.
DEVICE_CLASS = 0
IFACES = [0, 1, 2]
REPORT_DESC = bytes([0x05,0x01,0x09,0x05,0xa1,0x01,0x85,0x09,0x06,0x00,0xff,0x09,0x01,0x15,0x00,0x26,0xff,0x00,0x75,0x08,0x95,0x3f,0x81,0x02,0xc0])
_filler = b"".join(bytes([9,4,2,a,1,0xff,0,0,0]) + bytes([7,5,0x83,1,0,0,4]) for a in range(0, 14))
CONFIG_BODY = (bytes([9,4,0,0,1,3,0,0,0]) + hid_desc(len(REPORT_DESC)) + bytes([7,5,0x81,3,64,0,4]) +
               bytes([9,4,1,0,2,0xff,0,0,0]) + bytes([7,5,0x02,2,64,0,0, 7,5,0x82,2,64,0,0]) + _filler)
# adversarial OPT: nak = from bulk cmd #3 on every OUT is NAKed (device hangs the pipe); late1 = 20 alt settings of interface 0 before
# interface 1, so interface 1 starts past the driver's 256-byte buffer; zerolen = a bLength 0 byte appended inside wTotalLength.
if OPT == "late1":
    _pre = b"".join(bytes([9,4,0,a,1,0xff,0,0,0]) + bytes([7,5,0x83,1,0,0,4]) for a in range(1, 21))
    CONFIG_BODY = (bytes([9,4,0,0,1,3,0,0,0]) + hid_desc(len(REPORT_DESC)) + bytes([7,5,0x81,3,64,0,4]) + _pre +
                   bytes([9,4,1,0,2,0xff,0,0,0]) + bytes([7,5,0x02,2,64,0,0, 7,5,0x82,2,64,0,0]))
if OPT == "zerolen":
    CONFIG_BODY = CONFIG_BODY + bytes([0, 0, 0, 0])
OUTS = [0]

def phases(ep, n):
    if ep != 1: return None
    r = bytearray(64); r[0] = 9; r[1] = n & 255
    r[5:11] = bytes([0x00, 0x08, 0x80, 0x00, 0x08, 0x80])   # sticks centred (12-bit 0x800)
    return bytes(r)

class Device(Base):
    def on_out(self, ep, data):
        OUTS[0] += 1
        k = OUTS[0]
        bad = (OPT == "once" and k == 3) or (OPT == "always" and k >= 3)
        if OPT == "nak" and k >= 3: log("BULK OUT #%d NAK" % k); return NAK
        log("BULK OUT #%d ep %d cmd %s %s" % (k, ep, bytes(data)[:1].hex(), "-> STALL" if bad else "ok"))
        return STALL if bad else ACK
