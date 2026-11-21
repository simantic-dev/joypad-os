# PR 226 adversarial: usb2wiiext (USB host -> Wii extension port I2C slave 0x52)

Binary: sim-main. PR-only target (main has no usb2wiiext), `usb2wiiext_pico` built from ci-pr-226 (6fbbb14e). Script `scenarios/adv/226_adv.sh`; Wii console = `peers/wii_master.py` (config `start_ms`, `poll_ms`); DS4 peer on the native host. Logs `results/226/adv/`.

| # | Attack | result |
|---|---|---|
| 1 | console probes at 2 ms after reset (before USB enumeration) | slave NACKs the first four accesses (0xF0, 0xFB, ID, cal; reads NACK until t=0.053 s), answers from 53 ms on with a valid neutral Classic Pro report; the master's init writes were never ACKed so a console that does not retry would have latched "no extension" |
| 2 | console polls every 1 ms (16x normal) for 8 s | init ACKed, ID `0100a4200101`, cal ok, all DS4 phases decoded (B, sticks, ZL...), no NACK, no fault |
| 3 | no pad attached at all | ID/cal ok, neutral report `a0201000ffff` (sticks centred, no buttons), no fault |
Not run: pad hot-unplug while a button is held (the RP2040 host model has no run-time unplug), two pads (one native host port, `MAX_PLAYER_SLOTS 1`).

## Findings
None attributable to the PR code (NONE). Attack 1 is the boot-time window before `wii_device_init()` (about 50 ms in the sim, mostly stdio/flash init); the PR comment says the slave comes up before the router and USB host stack, which holds, but a console probing earlier than that cannot be helped. The output stage `wii_ext_device.c` is unchanged by the PR and untested here beyond these attacks.
