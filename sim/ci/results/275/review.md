# PR 275 review draft: DS4 touchpad normalisation, Nacon Revolution Pro 2, calibration request

Verdict: DEMONSTRATED

## What was tested and how
I ran the firmware (usb2usb remapper B, native RP2040 USB host) on main (9fa79f45) and on the PR (e19d3543, not behind main) in Simantic's RP2040 simulator. The USB peers are scripted devices built from public descriptor dumps (DS4/DualSense dsremap docs and the dogtopus DualSense gist, report layouts per Linux hid-playstation.c). They are not captures from physical units. Simulator: Simantic's RP2040 simulator (pyrite), a local unreleased build of main plus the PIO-USB host model branches (USB.PioUsb), used for every run below. A scripted DualShock 4 (054c:09cc, 225-byte configuration, 507-byte report descriptor, 64-byte input report 0x01) sits on the host port and moves through time-based phases; at 12 s one finger goes to the far corner (1919,941), at 13 s two fingers go to the centre and the quarter point. What B forwards to the output side is decoded from its uart link frames. The same run was repeated with the VID/PID set to the Nacon 146b:0d02, with the DS4 peer stalling GET_REPORT 0x02 and keeping accel at 0 until it has been requested, as the PR text describes. Script: scenarios/275.sh, logs: results/275/review/.

## Results
Touch coordinates as seen after the host driver (field range 0..65535):

| case | main | PR |
|---|---|---|
| finger 1 at (1919,941) | touch_x=1919, touch_y=941 | touch_x=65535, touch_y=65465 |
| two fingers (960,480)/(480,235) | 960,480 / 471,235 | 32784,16392 / 32767,16348 |

Raw 1919x942 values are passed through on main, so every output mode scales them down a second time; the PR normalises them to the full range. Genuine DS4: Player 1 assigned as Sony DualShock 4 on both; buttons, sticks and triggers unchanged (console logs otherwise identical apart from addresses).

Nacon 146b:0d02: main logs DEVICE:[HID Gamepad] and no touch or motion frames; the PR logs DEVICE:[Sony DualShock 4], forwards the same normalised touch values, and sends rumble/LED output reports to the pad.

Calibration request: PR peer log shows "GET_REPORT type 3 id 2 len 37 -> 37 bytes" for the genuine DS4 (reply ignored, nothing else changes) and "-> STALL" for the Nacon (init continues); no GET_REPORT on main.

## Bugs or regressions
None found. One observation: y is divided by 942 (the touchpad height) while x uses 1919 (its maximum), so y=941 maps to 65465, not 65535. This matches ds4_bt.c (same constants), so it is not new, and the loss is 0.1%.

## Not covered
- The Nacon descriptor is not a dump: the PR states its HID descriptor is byte-identical to a genuine DS4, so the DS4 descriptor is reused under the Nacon VID/PID. Its real configuration descriptor and strings are unknown to me.
- The "accel stays 0 until the request" quirk is modelled from the PR text only. Because main does not use the DS4 driver for the Nacon, the accel-before-request failure cannot be shown on main.
- Native USB host only (the PR's changed code is host-controller independent); PIO-USB host not run. No PS5/Switch output-mode check of the scaled touch values. No physical hardware.
