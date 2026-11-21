# DualShock 4 v2 (USB, VID/PID set by run_pio.sh). Everything below is from public sources, none from Joypad:
#  * Device, 225-byte configuration (3 audio interfaces + HID interface 3, EP 0x84/0x03, bInterval 5) and the 507-byte HID
#    report descriptor: a real 054c:09cc dump published in dsremap's docs
#    https://dsremap.readthedocs.io/en/latest/reverse.html (decoded with eleccelerator's usbdescreqparser).
#  * Input report 0x01 layout (64 bytes): Linux drivers/hid/hid-playstation.c struct dualshock4_input_report_usb,
#    cross-checked with dsremap's offset table (dpad+faces @5, shoulder @6, PS/touchpad/counter @7, L2/R2 @8/9,
#    timestamp @10, gyro @13, accel @19, battery @30, touch count @33, touch reports @34).
#  * Feature reports: GET_REPORT 0x02 (37 B calibration), 0xa3 (49 B firmware), 0x12 (16 B pairing) sized per
#    hid-playstation.c DS4_FEATURE_REPORT_*; field order per dsremap "Known feature reports". The values (gyro/accel
#    +-8192 span, speed 540/540, dates, MAC) are representative of a real unit, not a particular unit's dump.
#  * Strings: "Sony Computer Entertainment" / "Wireless Controller" (lsusb/usb.ids names of 054c:09cc).
import struct
DEVICE_CLASS = 0
IFACES = [0]
MANUFACTURER = "Sony Computer Entertainment"
PRODUCT = "Wireless Controller"
REPORT_DESC = (bytes.fromhex("05010905a10185010930093109320935150026ff007508950481020939150025")
    + bytes.fromhex("073500463b016514750495018142650005091901290e150025017501950e8102")
    + bytes.fromhex("0600ff0920750695011500257f8102050109330934150026ff00750895028102")
    + bytes.fromhex("0600ff09219536810285050922951f9102850409239524b102850209249524b1")
    + bytes.fromhex("02850809259503b102851009269504b102851109279502b10285120602ff0921")
    + bytes.fromhex("950fb102851309229516b10285140605ff09209510b10285150921952cb10206")
    + bytes.fromhex("80ff858009209506b102858109219506b102858209229505b102858309239501")
    + bytes.fromhex("b102858409249504b102858509259506b102858609269506b102858709279523")
    + bytes.fromhex("b10285880928953fb102858909299502b102859009309505b102859109319503")
    + bytes.fromhex("b102859209329503b10285930933950cb10285940934953fb10285a009409506")
    + bytes.fromhex("b10285a109419501b10285a209429501b10285a309439530b10285a40944950d")
    + bytes.fromhex("b10285f00947953fb10285f10948953fb10285f20949950fb10285a7094a9501")
    + bytes.fromhex("b10285a8094b9501b10285a9094c9508b10285aa094e9501b10285ab094f9539")
    + bytes.fromhex("b10285ac09509539b10285ad0951950bb10285ae09529501b10285af09539502")
    + bytes.fromhex("b10285b00954953fb10285e009579502b10285b30955953fb10285b40955953f")
    + bytes.fromhex("b10285b50956953fb10285d00958953fb10285d40959953fb102c0"))
CONFIG_FULL = (bytes.fromhex("0902e100040100c0fa0904000000010100000a2401000147000201020c240201")
    + bytes.fromhex("01010602030000000a2406020101030000000924030302040402000c24020402")
    + bytes.fromhex("0403010000000009240605040103000009240306010101050009040100000102")
    + bytes.fromhex("0000090401010101020000072401010101000b24020102021001007d00090501")
    + bytes.fromhex("0984000100000725010000000009040200000102000009040201010102000007")
    + bytes.fromhex("2401060101000b24020101021001803e00090582052200010000072501000000")
    + bytes.fromhex("0009040300020300000009211101000122fb0107058403400005070503034000")
    + bytes.fromhex("05"))

def _cal():
    b = struct.pack("<7h", 0, 0, 0, 8192, -8192, 8192, -8192)                        # gyro bias xyz, x max/min, y max/min
    b += struct.pack("<2h", 8192, -8192) + struct.pack("<2h", 540, 540)              # z max/min, speed max/min
    b += struct.pack("<6h", 8192, -8192, 8192, -8192, 8192, -8192)                   # accel x,y,z max/min
    return bytes([2]) + b + bytes(2)                                                 # 37 bytes
def _fw():
    b = bytearray(49); b[0] = 0xa3
    b[1:12] = b"Sep 21 2017"; b[12:20] = b"04:50:17"
    b[35:37] = struct.pack("<H", 0x0100); b[41:43] = struct.pack("<H", 0x0054)       # hw / fw version (hid-playstation offsets)
    return bytes(b)
def _pair():
    return bytes([0x12, 0xa0, 0x5a, 0x1c, 0x31, 0x6e, 0x9d, 0x08, 0x25, 0x00]) + bytes(6)   # own BD_ADDR, 08 25 00, never paired
GET_REPORT_REPLY = {(3, 2): _cal(), (3, 0xa3): _fw(), (3, 0x12): _pair()}
if PID == 0x0d02: GET_REPORT_REPLY = {}   # Nacon Revolution Pro 2: does not implement 0x02, stalls it (PR 275 text)

# adversarial options (OPT, comma separated): calbig = 0x02 reply 64 B, calshort = 3 B, calempty = 0 B, calstall = STALL,
# touchmax = fingers at the 12-bit maximum 4095/4095 (out of the 1919x942 pad range), touchneg = 0,0
_O = set(OPT.split(",")) if OPT else set()
if "calbig" in _O: GET_REPORT_REPLY[(3, 2)] = bytes([2]) + bytes(range(63))
if "calshort" in _O: GET_REPORT_REPLY[(3, 2)] = bytes([2, 1, 2])
if "calempty" in _O: GET_REPORT_REPLY[(3, 2)] = b""
if "calstall" in _O: GET_REPORT_REPLY.pop((3, 2), None)
TW, TH = (4095, 4095) if "touchmax" in _O else (1920, 942)      # touchpad extent (hid-playstation DS4_TOUCHPAD_WIDTH/HEIGHT)

def touch(x, y):  # 12-bit x, 12-bit y packed in 3 bytes (hid-playstation DS4_TOUCH_POINT_X/Y)
    return [x & 255, ((y & 15) << 4) | (x >> 8), y >> 4]

def report(n, cross=0, f1=None, f2=None, lx=128, ly=128, rx=128, ry=128, l2=0, r2=0):
    r = bytearray(64)
    r[0] = 1
    r[1:5] = bytes([lx, ly, rx, ry])
    r[5] = 8 | (cross << 5)                     # hat released (8), cross = bit 5
    r[6] = (l2 > 127) << 2 | (r2 > 127) << 3    # L2/R2 digital bits follow the analog triggers
    r[7] = (n & 63) << 2                        # PS/touchpad clear, 6-bit counter in bits 2..7
    r[8], r[9] = l2, r2
    r[10:12] = struct.pack("<H", (n * 5000 * 1000 // 5333) & 0xffff)   # 5 ms per report in 5.33 us units
    r[13:19] = struct.pack("<3h", 0x10, 0x20, 0x30)
    if CAL[0] or PID != 0x0d02: r[19:25] = struct.pack("<3h", 0, 0, 8192)   # accel z = 1 g; the Nacon only after the 0x02 request
    r[30] = 0x1b                                # cable (bit 4) + battery level 11
    r[33] = 1                                   # one touch report
    r[34] = n & 255                             # touch report timestamp
    for off, f in ((35, f1), (39, f2)):
        r[off] = (n & 127) if f else 0x80       # bit 7 set = no finger
        if f: r[off + 1:off + 4] = bytes(touch(*f))
    for off in (44, 53): r[off] = r[off + 4] = 0x80   # touch reports 1 and 2: both points released
    return bytes(r)

# Polls come every bInterval = 5 ms (200/s): 1 s = 200 polls. The input phases are time based on that clock.
def phases(ep, n):
    if ep != 4: return None
    s = n / 200.0
    if s < 3: return report(n)
    if s < 4: return report(n, cross=1)                                     # Cross
    if s < 5: return report(n)
    if s < 6: return report(n, lx=255, ly=0)                                # left stick up-right
    if s < 7: return report(n)
    if s < 8: return report(n, rx=0, ry=255)                                # right stick down-left
    if s < 9: return report(n)
    if s < 10: return report(n, l2=255)                                     # L2 fully pressed
    if s < 11: return report(n, r2=128)                                     # R2 half pressed
    if s < 12: return report(n)
    if s < 13: return report(n, f1=(TW - 1, TH - 1))                        # finger 1 in the far corner
    if s < 14: return report(n, f1=(TW // 2, TH // 2), f2=(TW // 4, TH // 4))
    return report(n)

CAL = [False]

def got_report(i):
    if i == 2: CAL[0] = True
