# Scripted BLE HID-over-GATT gamepad (pyrite Wireless.ScriptedBlePeer), the Python twin of sim/peers/nrf_pad (Zephyr).
# Same name, report map and report sequence. Needs pyrite with SMP/LL encryption in the scripted peer (#3818) and
# `Peer.adv_data` (raw AD structures in the ADV_IND, which this peer needs: Joypad connects on the HID UUID/appearance).
# Like the Zephyr pad it demands an encrypted link for the report, its CCC and (via ATT error 0x0F) so the central pairs.
import struct

ERR, MTU_RSP = 0x01, 0x03
FIND_INFO, FIND_INFO_RSP, FIND_TYPE, FIND_TYPE_RSP = 0x04, 0x05, 0x06, 0x07
BY_TYPE, BY_TYPE_RSP, READ, READ_RSP, BLOB, BLOB_RSP = 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D
BY_GROUP, BY_GROUP_RSP, WRITE, WRITE_RSP, WRITE_CMD = 0x10, 0x11, 0x12, 0x13, 0x52
NOT_FOUND, INSUFF_ENC, INVALID_OFFSET, NOT_SUPPORTED = 0x0A, 0x0F, 0x07, 0x06
ATT_MTU = 23

PRIMARY, CHAR, CCC, REPORT_REF = 0x2800, 0x2803, 0x2902, 0x2908
HIDS, HID_INFO, REPORT_MAP, REPORT, CTRL_POINT = 0x1812, 0x2A4A, 0x2A4B, 0x2A4D, 0x2A4C
R, WNR, N = 0x02, 0x04, 0x10

REPORT_MAP_VALUE = bytes([
    0x05, 0x01, 0x09, 0x05, 0xA1, 0x01, 0x85, 0x01,
    0x05, 0x09, 0x19, 0x01, 0x29, 0x10, 0x15, 0x00, 0x25, 0x01, 0x75, 0x01, 0x95, 0x10, 0x81, 0x02,
    0x05, 0x01, 0x09, 0x30, 0x09, 0x31, 0x09, 0x32, 0x09, 0x35,
    0x15, 0x00, 0x26, 0xFF, 0x00, 0x75, 0x08, 0x95, 0x04, 0x81, 0x02, 0xC0])

STEPS = [bytes([b0, b1, x, y, 128, 128]) for b0, b1, x, y in (
    (0, 0, 128, 128), (1, 0, 128, 128), (0, 0, 128, 128), (2, 2, 128, 128),
    (0, 0, 128, 128), (0, 0, 255, 0), (0, 0, 128, 128))]

# (handle, type, value, needs_encryption)
ATTRS = [
    (0x01, PRIMARY, struct.pack('<H', HIDS), False),
    (0x02, CHAR, struct.pack('<BHH', R, 0x03, HID_INFO), False),
    (0x03, HID_INFO, bytes([0x00, 0x00, 0x00, 0x02]), False),
    (0x04, CHAR, struct.pack('<BHH', R, 0x05, REPORT_MAP), False),
    (0x05, REPORT_MAP, REPORT_MAP_VALUE, False),
    (0x06, CHAR, struct.pack('<BHH', R | N, 0x07, REPORT), False),
    (0x07, REPORT, b'', True),
    (0x08, CCC, b'\x00\x00', True),
    (0x09, REPORT_REF, bytes([1, 1]), False),
    (0x0A, CHAR, struct.pack('<BHH', WNR, 0x0B, CTRL_POINT), False),
    (0x0B, CTRL_POINT, b'\x00', False),
]
GROUPS = [(0x01, 0x0B, HIDS)]
H_REPORT, H_CCC = 0x07, 0x08


def u16(v):
    return struct.pack('<H', v)


class Peer:
    adv_data = (bytes([2, 0x01, 0x06]) + bytes([8, 0x09]) + b'Sim Pad'  # flags, name
                + bytes([3, 0x03, 0x12, 0x18]) + bytes([3, 0x19, 0xC4, 0x03]))  # HID UUID, appearance gamepad
    io_capabilities = 'NoInputNoOutput'  # LESC Just Works

    def __init__(self, ctx):
        self.ctx = ctx
        self.attrs = {a[0]: list(a) for a in ATTRS}
        self.encrypted = False
        self.subscribed = False
        self.step = 0

    def on_connect(self):
        self.encrypted = self.subscribed = False
        self.attrs[H_CCC][2] = b'\x00\x00'
        self.ctx.info('connected')

    def on_disconnect(self, reason):
        self.ctx.cancel_timer()
        self.ctx.info('disconnected 0x%02x' % reason)

    def on_pairing_request(self, info):
        self.ctx.info('pairing request %s' % info)

    def on_paired(self, keys):
        self.ctx.info('paired sc=%s authenticated=%s' % (keys['sc'], keys['authenticated']))

    def on_encrypted(self):
        self.encrypted = True
        self.ctx.info('link encrypted')

    def on_timer(self):
        if not self.subscribed:
            return
        self.ctx.info('pad report %d: %s' % (self.step, STEPS[self.step].hex()))
        self.ctx.notify(H_REPORT, STEPS[self.step])
        self.step = (self.step + 1) % len(STEPS)

    def _err(self, pdu, handle, code):
        self.ctx.send(bytes([ERR, pdu[0]]) + u16(handle) + bytes([code]))

    def _value(self, h):
        return self.attrs[h][2]

    def on_att(self, pdu):
        op = pdu[0]
        h = pdu[1] | pdu[2] << 8 if len(pdu) >= 3 else 0
        if op == BY_GROUP:
            start, end, t = h, pdu[3] | pdu[4] << 8, pdu[5] | pdu[6] << 8
            for s, e, u in GROUPS:
                if t == PRIMARY and start <= s <= end:
                    return self.ctx.send(bytes([BY_GROUP_RSP, 6]) + u16(s) + u16(e) + u16(u))
            self._err(pdu, h, NOT_FOUND)
        elif op == FIND_TYPE:
            start, end, t = h, pdu[3] | pdu[4] << 8, pdu[5] | pdu[6] << 8
            for s, e, u in GROUPS:
                if t == PRIMARY and start <= s <= end and pdu[7:9] == u16(u):
                    return self.ctx.send(bytes([FIND_TYPE_RSP]) + u16(s) + u16(e))
            self._err(pdu, h, NOT_FOUND)
        elif op == BY_TYPE:
            start, end, t = h, pdu[3] | pdu[4] << 8, pdu[5] | pdu[6] << 8
            hits = [a for a in sorted(self.attrs.values()) if a[1] == t and start <= a[0] <= end]
            if hits and hits[0][3] and not self.encrypted:
                return self._err(pdu, hits[0][0], INSUFF_ENC)
            if not hits:
                return self._err(pdu, h, NOT_FOUND)
            n = len(hits[0][2][:ATT_MTU - 4])
            out = bytearray([BY_TYPE_RSP, n + 2])
            for a in hits:
                if len(a[2][:ATT_MTU - 4]) != n or len(out) + n + 2 > ATT_MTU:
                    break
                out += u16(a[0]) + a[2][:n]
            self.ctx.send(bytes(out))
        elif op == FIND_INFO:
            end = pdu[3] | pdu[4] << 8
            out = bytearray([FIND_INFO_RSP, 1])
            for a in sorted(self.attrs.values()):
                if h <= a[0] <= end and len(out) + 4 <= ATT_MTU:
                    out += u16(a[0]) + u16(a[1])
            self.ctx.send(bytes(out)) if len(out) > 2 else self._err(pdu, h, NOT_FOUND)
        elif op in (READ, BLOB):
            off = pdu[3] | pdu[4] << 8 if op == BLOB else 0
            if h not in self.attrs:
                return self._err(pdu, h, NOT_FOUND)
            if self.attrs[h][3] and not self.encrypted:
                return self._err(pdu, h, INSUFF_ENC)
            v = self._value(h)
            if off > len(v):
                return self._err(pdu, h, INVALID_OFFSET)
            self.ctx.send(bytes([READ_RSP if op == READ else BLOB_RSP]) + v[off:off + ATT_MTU - 1])
        elif op in (WRITE, WRITE_CMD):
            if h not in self.attrs:
                return op == WRITE and self._err(pdu, h, NOT_FOUND)
            if self.attrs[h][3] and not self.encrypted:
                return op == WRITE and self._err(pdu, h, INSUFF_ENC)
            if h == H_CCC:
                self.attrs[h][2] = bytes(pdu[3:5]).ljust(2, b'\0')
                self.subscribed = bool(pdu[3] & 1)
                self.ctx.info('report notifications %s' % ('on' if self.subscribed else 'off'))
                self.ctx.cancel_timer()
                if self.subscribed:
                    self.ctx.schedule_periodic(100_000)
            if op == WRITE:
                self.ctx.send(bytes([WRITE_RSP]))
        elif op % 2 == 0 and not op & 0x40:
            self._err(pdu, h, NOT_SUPPORTED)  # an unanswered request stalls the client
