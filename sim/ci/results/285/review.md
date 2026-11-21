# PR 285 review draft: DualSense Edge (054c:0df2) on the USB host

Verdict: DEMONSTRATED

## What was tested and how
Firmware: usb2usb remapper B (native RP2040 USB host + uart link) and the usb2usb PIO-USB host build (joypad_usb_feather_rp2040, D+=GP16 D-=GP17, output mode Switch), each on main (9fa79f45) and on the PR (32d005c8, not behind main), in Simantic's RP2040 simulator. The USB peers are scripted devices built from public descriptor dumps (DS4/DualSense dsremap docs and the dogtopus DualSense gist, report layouts per Linux hid-playstation.c). They are not captures from physical units. Simulator: Simantic's RP2040 simulator (pyrite), a local unreleased build of main plus the PIO-USB host model branches (USB.PioUsb), used for every run below. No public USB descriptor dump of the Edge was used: the peer is the DualSense peer (227-byte configuration, 273-byte report descriptor, 64-byte input report 0x01) with product ID 0x0df2. The Edge's real descriptors may differ. Phases per second: Cross at 3 s, left stick, right stick, L2, R2, then touch. Script: scenarios/285.sh; logs results/285/review/ (native.*, pio.*). On the PIO host the device-side output was also captured with --usb-hid-tap usb.

## Results
| | main | PR |
|---|---|---|
| native: driver | DEVICE:[HID Gamepad], "Player 1 assigned: HID Gamepad" | DEVICE:[Sony DualSense], "Player 1 assigned: Sony DualSense" |
| PIO: driver | DEVICE:[HID Gamepad] | DEVICE:[Sony DualSense] |
| touch/motion (EXT frames to the output side) | none (0 frames) | 12 frames, finger at corner 65535/65535, two fingers 32784,16392 |
| rumble/LED output reports to the pad (OUT ep 3) | 0 | 2 (report 0x02) on native and PIO |
| trigger idle value (native, generic parser) | L2/R2 = 1 | L2/R2 = 0 |

Mount works on both; the device is claimed by a different driver. Buttons and sticks come out identical in both runs (PIO tap, Switch-mode reports: Cross 02 00 08 80 80 80 80 00, left stick right/up 00 00 08 ff 01 80 80 00, right stick left/down 00 00 08 80 80 01 ff 00, L2 40 .., R2 80 ..), because my peer's report layout is the DualSense layout the generic parser can already read. So what the PR gains here is touch, motion, rumble/LED, correct trigger idle, not button mapping; whether main misparses a real Edge is not shown.

## Bugs or regressions
None found.

## Not covered
The Edge's real descriptors (back paddles, function buttons, a different config or report layout, if any), the Edge's authentication or feature-report traffic, output-mode checks other than Switch on PIO, any physical hardware.
