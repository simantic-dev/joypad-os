#!/usr/bin/env python3
"""USB host on `sim --usb-raw`: ask the nRF52840 usb2usb device for its descriptors, log each result."""
import sys
from peer import Usb
u = Usb(int(sys.argv[1]))
for name, args in [("reset", None), ("device descriptor", (0x80, 6, 0x0100, 0, 18)),
                   ("config descriptor (9 B)", (0x80, 6, 0x0200, 0, 9)),
                   ("SET_ADDRESS 1", (0x00, 5, 1, 0, 0)), ("config descriptor after SET_ADDRESS", (0x80, 6, 0x0200, 0, 9))]:
    r = u.req(op="reset") if args is None else u.req(op="setup", bmRequestType=args[0], bRequest=args[1],
                                                       wValue=args[2], wIndex=args[3], wLength=args[4] if len(args) > 4 else 0)
    print(f"{name}: {r}")
