# DualSense (USB, VID/PID set by run_pio.sh). Public sources only:
#  * Device, 227-byte configuration (3 audio interfaces + HID interface 3, EP 0x84/0x03, bInterval 4) from the 054c:0ce6
#    dump in dsremap's docs https://dsremap.readthedocs.io/en/latest/reverse.html; the 273-byte HID report descriptor
#    is byte-identical to dogtopus's hidrd listing https://gist.github.com/dogtopus/894da226d73afb3bdd195df41b3a26aa
#    (compiled by gen/hidrd2bytes.py; 273 = the wDescriptorLength of the real config).
#  * Input report 0x01 (64 bytes): Linux hid-playstation.c struct dualsense_input_report: sticks @1..4, L2/R2 @5/6,
#    seq @7, buttons[4] @8..11 (hat+faces @8, shoulders/sticks @9, PS/touchpad/mute @10, edge @11), gyro @16, accel @22,
#    sensor timestamp @28, touch points @33, status @53. On the wire the upper bits of byte 10 carry a frame counter
#    (dsremap offset 10: "5 unknown bits"); the buttons live in bits 0..2, which is what an honest peer keeps clear.
#  * Feature reports 0x05 (41 B) / 0x09 (20 B) / 0x20 (64 B): sizes and field offsets from hid-playstation.c
#    DS_FEATURE_REPORT_*; values representative, not one unit's dump.
#  * Strings: "Sony Interactive Entertainment" / "DualSense Wireless Controller" (kernel log names of 054c:0ce6).
import struct
DEVICE_CLASS = 0
IFACES = [0]
MANUFACTURER = "Sony Interactive Entertainment"
PRODUCT = "DualSense Wireless Controller"
REPORT_DESC = (bytes.fromhex("05010905a1018501093009310932093509330934150026ff0075089506810206")
    + bytes.fromhex("00ff09209501810205010939150025073500463b016514750495018142650005")
    + bytes.fromhex("091901290f150025017501950f81020600ff0921950d81020600ff0922150026")
    + bytes.fromhex("ff0075089534810285020923952f9102850509339528b10285080934952fb102")
    + bytes.fromhex("850909249513b102850a0925951ab10285200926953fb102852109279504b102")
    + bytes.fromhex("85220940953fb10285800928953fb10285810929953fb1028582092a9509b102")
    + bytes.fromhex("8583092b953fb1028584092c953fb1028585092d9502b10285a0092e9501b102")
    + bytes.fromhex("85e0092f953fb10285f00930953fb10285f10931953fb10285f20932950fb102")
    + bytes.fromhex("85f40935953fb10285f509369503b102c0"))
CONFIG_FULL = (bytes.fromhex("0902e300040100c0fa0904000000010100000a2401000149000201020c240201")
    + bytes.fromhex("01010604330000000c24060201010300000000000924030301030402000c2402")
    + bytes.fromhex("0402040301000000000924060504010300000924030601010105000904010000")
    + bytes.fromhex("01020000090401010101020000072401010101000b2402010402100180bb0009")
    + bytes.fromhex("0501098801010000072501010000000904020000010200000904020101010200")
    + bytes.fromhex("00072401060101000b2402010202100180bb0009058205c40001000007250100")
    + bytes.fromhex("0000000904030002030000000921110100012211010705840340000407050303")
    + bytes.fromhex("400004"))

def _cal():
    b = bytes([5]) + struct.pack("<3h", 0, 0, 0)                                      # gyro bias pitch,yaw,roll
    b += struct.pack("<6h", 8192, -8192, 8192, -8192, 8192, -8192)                    # gyro +/- per axis
    b += struct.pack("<2h", 540, 540)                                                 # gyro speed +/-
    b += struct.pack("<6h", 8192, -8192, 8192, -8192, 8192, -8192)                    # accel x,y,z +/-
    return b + bytes(41 - len(b))
def _pair():
    mac = bytes([0xa0, 0x5a, 0x1c, 0x31, 0x6e, 0x9d])
    return bytes([9]) + mac + bytes([0x08, 0x25, 0x00]) + bytes(6) + bytes(4)         # own MAC, 08 25 00, host, crc32 (0 via USB)
def _fw():
    b = bytearray(64); b[0] = 0x20
    b[1:20] = b"Mar 18 202113:57:46"
    b[24:28] = struct.pack("<I", 0x00000300); b[28:32] = struct.pack("<I", 0x01000420)   # hw / fw version (hid-playstation offsets)
    b[44:46] = struct.pack("<H", 0x0200)                                              # update version
    return bytes(b)
GET_REPORT_REPLY = {(3, 5): _cal(), (3, 9): _pair(), (3, 0x20): _fw()}

TW, TH = 1920, 1080     # DS_TOUCHPAD_WIDTH/HEIGHT

def touch(x, y):
    return [x & 255, ((y & 15) << 4) | (x >> 8), y >> 4]

def report(n, cross=0, f1=None, f2=None, lx=128, ly=128, rx=128, ry=128, l2=0, r2=0):
    r = bytearray(64)
    r[0] = 1
    r[1:7] = bytes([lx, ly, rx, ry, l2, r2])
    r[7] = n & 255                                # seq_number
    r[8] = 8 | (cross << 5)                       # hat released (8), cross = bit 5
    r[9] = (l2 > 127) << 2 | (r2 > 127) << 3      # L2/R2 digital
    r[10] = (n & 31) << 3                         # PS/touchpad/mute clear; frame counter in the upper bits
    r[16:22] = struct.pack("<3h", 0x10, 0x20, 0x30)
    r[22:28] = struct.pack("<3h", 0, 0, 8192)
    r[28:32] = struct.pack("<I", n * 4000 * 3 & 0xffffffff)
    for off, f in ((33, f1), (37, f2)):
        r[off] = (n & 127) if f else 0x80
        if f: r[off + 1:off + 4] = bytes(touch(*f))
    r[53] = 0x1a                                  # status[0]: battery 10, charging nibble 1
    return bytes(r)

# Polls come every bInterval = 4 ms (250/s): 1 s = 250 polls. The input phases are time based on that clock.
# adversarial OPT: paddle = Edge byte 10 bits 6/7/4/5 (L/R paddle, L/R Fn per SDL/hid-playstation) held 3-6 s, nothing else changing;
# short = 10-byte input report from 3 s on; zero = 1-byte report (id only) from 3 s on.
def phases(ep, n):
    if ep != 4: return None
    s = n / 250.0
    if OPT == "paddle" and 3 <= s < 7:
        r = bytearray(report(0)); r[10] = (0x40, 0x80, 0x10, 0x20)[int(s - 3)]; return bytes(r)
    if OPT == "short" and s >= 3: return report(n)[:10]
    if OPT == "zero" and s >= 3: return bytes([1])
    if s < 3: return report(n)
    if s < 4: return report(n, cross=1)
    if s < 5: return report(n)
    if s < 6: return report(n, lx=255, ly=0)
    if s < 7: return report(n)
    if s < 8: return report(n, rx=0, ry=255)
    if s < 9: return report(n)
    if s < 10: return report(n, l2=255)
    if s < 11: return report(n, r2=128)
    if s < 12: return report(n)
    if s < 13: return report(n, f1=(TW - 1, TH - 1))
    if s < 14: return report(n, f1=(TW // 2, TH // 2), f2=(TW // 4, TH // 4))
    return report(n)

# Live mode (sim/live, control port): set_property("pad", {"buttons": [b8, b9, b10], "hat": 0..8,
# "sticks": [lx, ly, rx, ry], "triggers": [l2, r2]}) replaces the timeline above; bytes 8..10 as report 0x01
# (b8 upper nibble = square/cross/circle/triangle, b9 = L1 R1 L2 R2 Create Options L3 R3, b10 = PS touchpad mute).
class Device(Base):
    pad = None

    def set_property(self, name, value):
        if name != "pad": raise KeyError(name)
        self.pad = value
        log("pad", value)

    def get_property(self, name):
        if name != "pad": raise KeyError(name)
        return self.pad

    def on_in(self, ep):
        if self.pad is None or ep != 4: return Base.on_in(self, ep)
        n = self.polls[ep] = self.polls.get(ep, 0) + 1
        p = self.pad
        r = bytearray(report(n, lx=p["sticks"][0], ly=p["sticks"][1], rx=p["sticks"][2], ry=p["sticks"][3],
                             l2=p["triggers"][0], r2=p["triggers"][1]))
        b8, b9, b10 = p["buttons"]
        r[8] = (b8 & 0xF0) | (p["hat"] & 0x0F)
        r[9] = b9
        r[10] = (r[10] & 0xF8) | (b10 & 7)
        return bytes(r)
