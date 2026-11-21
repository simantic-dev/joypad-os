#!/usr/bin/env python3
"""Both ends of the live page, on http://127.0.0.1:<http_port>/:
  POST /pad {"buttons": JP_BUTTON_* bits, "analog": [lx, ly, rx, ry, lt, rt]} -> one Joypad UART host INPUT_EVENT
       frame [0xAA][LEN][TYPE][PAYLOAD][CRC8] (src/core/uart/uart_protocol.h) on `sim --uart-tcp uart0`;
  GET  /  -> the latest HID report the USB console (this script, on `sim --usb-raw`) got, Switch/HORI 8-byte layout.
usage: bridge.py <usb_raw_port> <uart_tcp_port> <http_port>"""
# shortcut: the pad goes over --uart-tcp because pyrite's ScriptedUartPeer cannot attach to the RP2040 PL011 yet;
# move it to a control-port "pad" property on a UART peer once it can.
import json, socket, struct, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, __import__("os").path.dirname(__file__) + "/.."); from peer import Usb

def crc8(data):
    c = 0
    for b in data:
        c ^= b
        for _ in range(8):
            c = ((c << 1) ^ 0x07) & 0xFF if c & 0x80 else (c << 1) & 0xFF
    return c


def frame(ptype, payload):
    body = bytes([len(payload), ptype]) + payload
    return b"\xAA" + body + bytes([crc8(body)])


def frame(ptype, payload):
    body = bytes([len(payload), ptype]) + payload
    return b"\xAA" + body + bytes([crc8(body)])


assert crc8(b"123456789") == 0xF4  # CRC-8/SMBUS, as joypad-mcp's transport.ts

state = {"report": None, "t_us": 0, "wall": 0.0, "t0_us": None, "wall0": None}


def pump(u):
    while chunk := u.s.recv(65536):
        u.buf += chunk
        *lines, u.buf = u.buf.split(b"\n")
        for l in lines:
            m = json.loads(l) if l.strip() else {}
            if m.get("event") == "in":
                if state["t0_us"] is None:
                    state["t0_us"], state["wall0"] = m.get("t_us", 0), time.time()
                state.update(report=m["data"], t_us=m.get("t_us", 0), wall=time.time())
    sys.exit("usb-raw closed")


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        v = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        a = [max(0, min(255, int(x))) for x in v.get("analog", [128, 128, 128, 128, 0, 0])][:6]
        # uart_input_event_t: player 0, device_type GAMEPAD (0), buttons, analog[6], delta_x, delta_y
        uart.sendall(frame(0x10, struct.pack("<BBI6Bbb", 0, 0, int(v.get("buttons", 0)) & 0xFFFFFFFF, *a, 0, 0)))
        self.do_GET()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        r, el = state["report"], time.time() - (state["wall0"] or time.time())
        body = {"connected": r is not None, "t_us": state["t_us"],
                "speed": (state["t_us"] - (state["t0_us"] or 0)) / 1e6 / el if el > 1 else None}
        if r:
            b = bytes.fromhex(r)
            body.update(buttons=int.from_bytes(b[0:2], "little"), hat=b[2], sticks=list(b[3:7]), hex=r)
        out = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


uart = socket.create_connection(("127.0.0.1", int(sys.argv[2])))
threading.Thread(target=lambda: [None for _ in iter(lambda: uart.recv(4096), b"")], daemon=True).start()  # drain the firmware log
u = Usb(int(sys.argv[1])); u.enumerate()
threading.Thread(target=pump, args=(u,), daemon=True).start()
print(f"console: enumerated, serving http://127.0.0.1:{sys.argv[3]}/", flush=True)
ThreadingHTTPServer(("127.0.0.1", int(sys.argv[3])), H).serve_forever()
