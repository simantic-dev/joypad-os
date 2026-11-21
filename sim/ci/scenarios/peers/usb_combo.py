# Composite device: HID boot mouse (interface 0, EP 0x81) + generic HID gamepad (interface 1, EP 0x82). VID/PID are not in any driver table.
# OPT (comma list): mousezero = the mouse interface streams all-zero reports from the first poll (idle chatter); mousejit = +-1 counts.
# The pad presses button 1 from poll 100 to 150 and again 250-300.
DEVICE_CLASS = 0
IFACES = [0, 1]
_O = set(OPT.split(",")) if OPT else set()
MOUSE_DESC = bytes([0x05,0x01,0x09,0x02,0xa1,0x01,0x09,0x01,0xa1,0x00,0x05,0x09,0x19,0x01,0x29,0x03,0x15,0x00,0x25,0x01,
  0x95,0x03,0x75,0x01,0x81,0x02,0x95,0x01,0x75,0x05,0x81,0x01,0x05,0x01,0x09,0x30,0x09,0x31,0x09,0x38,
  0x15,0x81,0x25,0x7f,0x75,0x08,0x95,0x03,0x81,0x06,0xc0,0xc0])
PAD_DESC = bytes([0x05,0x01,0x09,0x05,0xa1,0x01,0x05,0x09,0x19,0x01,0x29,0x08,0x15,0x00,0x25,0x01,0x75,0x01,0x95,0x08,0x81,0x02,
  0x05,0x01,0x09,0x30,0x09,0x31,0x15,0x00,0x26,0xff,0x00,0x75,0x08,0x95,0x02,0x81,0x02,0xc0])
REPORT_DESC = MOUSE_DESC
CONFIG_BODY = (bytes([9,4,0,0,1,3,1,2,0]) + hid_desc(len(MOUSE_DESC)) + bytes([7,5,0x81,3,4,0,8]) +
               bytes([9,4,1,0,1,3,0,0,0]) + hid_desc(len(PAD_DESC)) + bytes([7,5,0x82,3,3,0,8]))

if "swap" in _O:   # pad = interface 0 / EP 0x81, mouse = interface 1 / EP 0x82
    CONFIG_BODY = (bytes([9,4,0,0,1,3,0,0,0]) + hid_desc(len(PAD_DESC)) + bytes([7,5,0x81,3,3,0,8]) +
                   bytes([9,4,1,0,1,3,1,2,0]) + hid_desc(len(MOUSE_DESC)) + bytes([7,5,0x82,3,4,0,8]))
    REPORT_DESC = PAD_DESC
SW = "swap" in _O
def phases(ep, n):
    ep = {1: 2, 2: 1}[ep] if SW else ep
    if n in (1, 2, 3, 50, 400): log('poll ep', ep, n)
    if ep == 1:
        if "mousezero" in _O: return bytes(4)
        if "mousejit" in _O: return bytes([0, 1 if n & 1 else 255, 0, 0])
        return None
    if ep == 2:
        if n in (1, 100, 250): log('pad poll', n)
        b = 1 if (100 <= n < 150 or 250 <= n < 300) else 0
        return bytes([b, 128, 128])
    return None

class Device(Base):
    def on_setup(self, setup, data):
        if setup[1] == 6 and setup[0] in (0x80, 0x81) and setup[3] == 0x22:
            idx = setup[4] | setup[5] << 8
            return (MOUSE_DESC if idx == 1 else PAD_DESC) if SW else (PAD_DESC if idx == 1 else MOUSE_DESC)
        return Base.on_setup(self, setup, data)
