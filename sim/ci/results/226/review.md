# PR 226 review draft: usb2wiiext (USB pad into the Wii extension port)

Verdict: DEMONSTRATED for the Pico target (usb2wiiext_pico), unencrypted mode; main has no equivalent to compare against.

## What was tested and how
I built `joypad_usb2wiiext_pico` from the PR (6fbbb14e, not behind main) and ran it in Simantic's RP2040 simulator. The USB peer is a scripted DualShock 4 built from public descriptor dumps (dsremap docs, report layout per Linux hid-playstation.c); it is not a capture from a physical unit. Simulator: Simantic's RP2040 simulator (pyrite), a local unreleased build. It sits on the native USB host port. The Wii console side is a Python peer (scenarios/peers/wii_master.py) that bit-bangs an I2C master on GP4 (SDA) and GP5 (SCL), with the RP2040 I2C0 target at pin level. It behaves as the wiibrew pages describe: 400 kHz, slave 0x52; unencrypted init (write 0x55 to 0xF0, 0x00 to 0xFB); read the 6-byte ID at 0xFA; read the 16-byte calibration at 0x20; then poll register 0x00 every 16.6 ms as write(address)+STOP then read. Sources: https://wiibrew.org/wiki/Wiimote/Extension_Controllers (init, ID, 0x52, 400 kHz) and https://wiibrew.org/wiki/Wiimote/Extension_Controllers/Classic_Controller (data formats 0x01 and 0x03, active-low buttons). The peer decodes each changed report. Runs: data format 0x01 (default) and 0x03 (the master writes 0xFE=0x03 first, as the Wii menu does). The DS4 pad moves through Cross (3 s), left stick up-right, right stick down-left, L2 full, R2 half. Script: scenarios/226.sh; logs results/226/review/{fmt1,fmt3}.*.

## Results
- Init and identification: both writes ACKed; ID = 0100a4200101 (Classic Controller Pro); calibration block e11f80 e11f80 e11f80 e11f80 0000 55aa with a valid checksum (0x55 / 0xaa as the source comment says).
- Idle: 0x01 report a0201000ffff (all sticks centred, no buttons pressed).
- Format 0x01 decoded: Cross -> B pressed (a01f0f00ffbf); left stick up-right -> LX=56/63, LY=55/63; right stick down-left -> RX=4/31, RY=4/31; L2 full -> LT=31/31 and ZL pressed; R2 half -> RT=16/31 and ZR pressed. Buttons return to unpressed (ffff) after each phase.
- Format 0x03: same input gives LX/LY/RX/RY 128 idle, Cross -> B pressed, LT=255 + ZL, RT=128 + ZR.

## Bugs or findings
- Format 0x03 and format 0x01 disagree on the X axes for the same stick position: left stick pushed right gives LX=56 (high) in 0x01 but LX=32 (low) in 0x03; right stick pushed left gives RX=4 (low) in 0x01 and RX=224 (high) in 0x03. The Y axes agree. The firmware comment in wii_ext_device.c says the X inversion is empirical from the Wii menu, and wiibrew does not give an axis direction, so I cannot tell which is right. This code is on main already (bt2wiiext); the PR only reuses it.
- Neutral drift of one count: after the first input event idle LY/RY become 31 (and 127 in format 0x03) instead of the seeded 32 (128).
- Not an error: L2 and R2 both raise the analog trigger and the digital ZL/ZR bit.

## Not covered
- The KB2040 target (joypad_usb2wiiext) was not built or run; only the Pico target.
- Encrypted mode (0xF0=0xAA key exchange), the Wii System Menu's real polling pattern, 5 V supply (the PR says it does not address it), real I2C timing margins; the simulated bus is a Python bit-bang master, not a Wiimote.
- main cannot be compared: it has no USB-input Wii target, and the shared output stage (wii_ext_device.c) ships only in bt2wiiext on a Pico W, which this model does not run.
- Controllers other than a DS4 over USB. No physical hardware.
