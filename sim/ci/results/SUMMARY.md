# Joypad OS upstream PRs on the simulator

RP2040 usb2usb remapper (PS5 mode, scripted USB host + UART input) and nRF52840 bt2usb (BLE HID pad), pyrite 0.10.5. 13 checks per PR; `main` passes 13/13.

| PR | Title | Result | Covered |
|---|---|---|---|
| #305 | feat(switch_bt): pair over CDC and show a live console link on the LED | not_exercised | no. `cdc_commands.c` is compiled into both the RP2040 usb2usb and the nRF bt2usb builds (object files present), but the new BLE.PAIR branch  |
| #304 | add stadia controller to list of BLE controllers | not_exercised | no. Docs only; no code is compiled or run. |
| #302 | ci(nrf): pin build-nrf to ubuntu-24.04 (CMake 4 breaks NCS v3.1.0) | not_exercised | no. The change affects the GitHub runner image for CI only. The simulator harness builds on the local lane, not through the workflow. |
| #301 | docs(changelog): fold Unreleased into 2.5.0 ahead of the release | not_exercised | no. Changelog only; nothing compiled or run. |
| #296 | feat(usb/switch): SELECT+START triggers Capture in Switch mode | not_exercised | no. `switch_mode.c` is compiled into the RP2040 usb2usb build, but the RP2040 image is built with `USBD_DEFAULT_MODE=PS5` (ps5default.cmake) |
| #295 | fix(profile): keep autofire timing state alive across profile_apply ca | pass | partly. `usbd.c` is compiled into both builds and `apply_usbd_profile_player()` runs on every USB device report in the RP2040 (PS5 output) a |
| #294 | feat(gc): pressure-sensitive analog A/B in GameCube analog modes (#114 | not_exercised | no. profile.c is compiled into both builds, but the only caller is `gamecube_device.c`, which is not part of the usb2usb or bt2usb targets ( |
| #293 | 3DO: make silly pad mode reachable again (#254) | not_exercised | no. `usb23do/app.c` and `3do_device.c` are not in the usb2usb or bt2usb builds. The profile.c/h removal is compiled into the RP2040 build (i |
| #292 | fix(nuon): light the KB2040 NeoPixel on usb2nuon via PIO1 (#257) | not_exercised | no. The change applies only to the usb2nuon_kb2040 target. The harness builds usb2usb_remapper_v7_a and bt2usb, and neither uses that flag. |
| #291 | feat(ps3): square stick range in PS3 mode (#143) | not_exercised | no. `ps3_mode.c` is compiled into the RP2040 usb2usb build, but that image runs in PS5 output mode, so `ps3_mode_send_report()` is never cal |
| #290 | fix(bt): retry Xbox rumble when a BLE write is still in flight | not_exercised | partly. Both files are compiled into the nRF bt2usb build and the BLE HOGP pad path runs in the scenario (pairing, A, B+START, stick), but t |
| #289 | fix(3do): keep mouse motion the console hasn't polled yet | not_exercised | no. `3do_device.c` is not in the usb2usb or bt2usb builds (no 3do object in the RP2040 build dir), and the scenario has no 3DO console or mo |
| #288 | fix(router): give a mouse a player slot on movement in simple mode | not_exercised | no. `router.c` is compiled into both builds, so the new condition is evaluated, but it only changes behaviour for a mouse input. The scenari |
| #287 | fix(alpakka): don't run the button service on the touch sense pin | not_exercised | no. The change applies only to the controller_alpakka target. The harness builds usb2usb_remapper_v7_a and bt2usb. |
| #286 | fix(switch2): don't let a failed bulk transfer or long descriptor kill | not_exercised | no. The file is compiled into the RP2040 usb2usb remapper build, but the RP run never runs a USB host driver: peer.py is the USB host that e |
| #285 | fix(ds5): match the DualSense Edge on USB host | not_exercised | no. is_sony_ds5() is in the USB host path, which the RP2040 run does not exercise (no USB HID controller on the remapper's host port; see PR |
| #284 | docs(dreamcast): button map matches the code since 7d086d4e | not_exercised | no. Only comments and markdown; the Dreamcast device is not part of either scenario (it is a usb2dc target, not usb2usb or bt2usb). |
| #283 | docs(bt2n64): wire console power to VSYS, fix the 6-pin pinout | not_exercised | no. Documentation only; no firmware file is touched. |
| #282 | Add Pro Micro nRF52840 (nice!nano / SuperMini) board target | not_exercised | partly. The Feather bt2usb build and boot run the shared nRF files and the BTstack central, so the common build and boot compile and run. Th |
| #281 | feat(nrf): nice!nano / nRF52840 Pro Micro / SuperMini build target | not_exercised | no. The harness builds only the Feather bt2usb; the nice_nano branches are compiled out there and the nice_nano board is never built or boot |
| #279 | fix(bt): don't touch BTstack bonds before BT is started (usb2gc config | not_exercised | no. The guards run only when the CDC BT.STATUS or BT.BONDS.CLEAR commands call them, and neither scenario sends CDC commands. The usb2gc con |
| #277 | feat(bt): stop the central from grabbing every controller in the room | pass | partly. The nRF bt2usb central runs the changed btstack_host.c at default (AUTO) mode: the boot scan starts and the pad is discovered, paire |
| #276 | docs(usbd): correct PS4 and Switch output-mode VID:PID | not_exercised | no. Documentation only; the firmware descriptors are not changed. |
| #275 | fix(usb/ds4): normalize touchpad coordinates; add Nacon Revolution Pro | not_exercised | no. All three changed files are USB host code (sony_ds4.c, sony_ds4.h, hid.c). The RP2040 run has no USB HID controller on the remapper's ho |
| #226 | feat(wiiext): add usb2wiiext — USB controllers into the Wii extension  | not_exercised | no. The harness builds only usb2usb_remapper_v7_a and bt2usb, so the new usb2wiiext targets are never compiled, and the RP2040 and nRF scena |
| #203 | fix(ps3): restore the authentic 49-byte DualShock 3 input report | build_failed | no. The RP2040 build failed, so nothing ran. Even if it built, the RP run uses PS5 default output mode, so the PS3 descriptor is not the act |
| #194 | feat(nuon): add usb2nuon_rp2040zero target | build_failed | no. The RP2040 build fails before the PR's target is compiled, and the nRF bt2usb scenario does not build or run Nuon code. |
| #192 | fix(bt): bind NSO retro pads (SNES/NES/N64/Genesis) to the Switch driv | not_exercised | no. The driver is compiled into the nRF build and registers at boot ("[BTHID] Registered driver: Switch Pro" in nrf_ble.console.txt), but sw |

build_failed on #203/#194 is the harness forcing PS5 mode (USB_OUTPUT_MODE_PS5) on bases from before that mode existed, not the PRs.

## Targeted scenarios (main vs PR on the behaviour each PR changes)

2026-11-20 review pass (#275 #285 #286 #226 #203): real-descriptor DS4/DualSense peers on the review simulator (main + PIO-USB branches); drafts in results/<N>/review.md.

| PR | Verdict | Evidence |
|---|---|---|
| #285 DualSense Edge on USB host | DEMONSTRATED | 054c:0df2 native + PIO host: main `HID Gamepad`, PR `Sony DualSense`, touch + rumble decoded (peer = DS5 under Edge PID, not an Edge dump) |
| #275 DS4 touch / Nacon / calibration | DEMONSTRATED | touch (1919,941): main raw, PR 65535/65465; Nacon 146b:0d02 uses DS4 driver; GET_REPORT 0x02 sent |
| #286 Switch 2 USB init | DEMONSTRATED | 281-byte descriptor: main rejects, PR 18/18; failed-bulk retry shown on the PIO-USB host (native host cannot deliver the STALL) |
| #288 mouse slot (simple mode) | fix demonstrated | main assigns on click, drops 25 moves; PR assigns on first move |
| #291 PS3 square sticks | feature demonstrated | diagonal (218,38) -> (255,1) |
| #296 SELECT+START -> Capture | feature demonstrated | main MINUS+PLUS, PR CAPTURE |
| #295 autofire state | no difference | main works by luck: uninitialised `profile_out` reuses the same stack slot |
| #290 Xbox BLE rumble retry | fix demonstrated | main `status=0x0C`, stop lost; PR both writes arrive |
| #277 discovery policy | feature demonstrated (BLE) | PR `Discovery mode: OFF`, no rescan; Classic BT case not simulated |
| #279 bonds before BT start | partly demonstrated | PR refuses BT.BONDS.CLEAR with BT off; reported HardFault not reproduced |
| #226 usb2wiiext | DEMONSTRATED | pico target: DS4 over USB -> Classic Pro registers read by a Python Wii I2C master; ID/cal ok, buttons+sticks decode; format 0x03 X axes opposite to 0x01 (shared code) |
| #203 PS3 49-byte report | DEMONSTRATED | PR on main: 49 bytes, motion at offset 41 (hid-sony.c); main 50 bytes, motion at 42 |
| #305 switch_bt pairing | could not simulate | Pico W Classic BT only |

## Adversarial (2026-11-20, sim-main = origin/main 4b5b5aee8)

Per-PR detail in `results/<N>/adversarial.md`, scripts in `scenarios/adv/<N>_*.sh`. Binary: `public-demos/bin/sim-main` for every run; `sim-main-inover` was not built because no PIO-USB host run was made. Findings re-run twice, identical bytes/log lines.

| PR | attacks run | PR-INTRODUCED | PR-INCOMPLETE | pre-existing |
|---|---|---|---|---|
| #275 | 6 (touch range, 4 calibration reply shapes) | 0 | 0 | 0 |
| #285 | 4 (Edge paddles, short, 1-byte report) | 0 | 1 (Edge paddle/Fn buttons dropped) | 1 (no `len` check before memcpy, harmless) |
| #286 | 5 (NAK-forever bulk, late interface 1, zero-length, STALL) | 0 | 2 (hung bulk pipe wedges init; interface 1 past 256 B) | 0 |
| #277 | 7 (OFF mid-connect x5, mode fuzz) | 0 | 1 (BONDED has no effect on BLE, by reading) | 1 (`json_get_int` truncates 1.9) |
| #290 | 4 (response delay 150 ms/800 ms/2 s, flood) | 0 | 1 (stop dropped after 500 ms retry budget) | 0 |
| #226 | 3 (early probe, 1 ms poll, no pad) | 0 | 0 | 0 |
| #288 | 3 (idle mouse chatter, jitter) | 1 (idle mouse takes Player 1) | 0 | 0 |
| #203 | static (descriptor parse) | 0 | 0 | 0 |
| #295 | static | 0 | 0 | 0 (shared static in GC/N64/Nuon unverified) |
| #291 | exhaustive offline | 0 | 0 | 0 (cross-axis coupling noted) |

Real findings:
- #288 PR-INTRODUCED: `|| event->type == INPUT_TYPE_MOUSE` gives any mouse report a slot, even all-zero. Idle mouse is Player 1, the pad Player 2. `results/288/adv/mousezero.{main,288}.console.txt`, `scenarios/adv/288_adv.sh`. Fix: require nonzero delta/wheel/button.
- #290 PR-INCOMPLETE: after `RUMBLE_RETRY_TIMEOUT_MS` (500 ms) the stop is marked sent and never resent. Write response held 800 ms/2 s: pad gets START only. `results/290/adv/h16pair.290.pad.txt`, `scenarios/adv/290_adv.sh`.
- #286 PR-INCOMPLETE: bulk OUT NAKed forever leaves `xfer_pending` set, init stuck at cmd 3 (4236 NAKs); no timeout. `results/286/adv/nak.286.*`. Also interface 1 beyond byte 256 is not found (`late1`).
- #285 PR-INCOMPLETE: Edge Fn/paddle bits (byte 10 bits 4-7) are read as the frame counter, so presses produce no event and no player. `results/285/adv/paddle.285.*`. Layout from SDL, from memory.
- #277 PR-INCOMPLETE (by reading only): BONDED mode never touches the BLE adv path; OFF makes bonded BLE pads unreachable until BT.SCAN.

Skipped: #305 (Classic BT/Pico W), #304, #302, #301, #284, #283, #276 (docs/CI only), #109 (draft WIP), #192 (name-based match is Classic BT; spoof risk noted only: any device named "N64 Controller" etc. binds to the Switch driver), #279 (usb2gc CDC-mode NULL deref did not fault in the sim before; not repeated), #282/#281/#194/#292/#287/#293/#294/#289/#296 (board/target-specific builds the harness does not run or output-only changes; #289 read: the IRQ lock is valid only if `on_pio0_irq` runs on the same core as the USB update, which it does as far as the init path shows).

Simulator gaps hit (not fixed, no pyrite changes):
1. RP2040 native host: no run-time unplug/replug from the CLI or scenarios (`Rp2040Usb::plug` exists but is not exposed), so replug/leak attacks and power-on-vs-hot-plug cannot be run. `ScriptedUsbDevice` cannot NAK a control data stage (`setup()` returns data or STALL only).
2. Bulk OUT STALL on the native host (#286 `always`): no completion reaches the firmware callback after cmd 3, so the PR retry path cannot be seen there.
3. Scripted BLE peers share one fixed advertising address (C1:23:45:67:89:AB), so several advertisers or stranger-vs-bonded cannot be simulated.
4. Composite device with the gamepad as HID instance 1: that endpoint is polled once and never again while instance 0 keeps being polled (same on main). Firmware re-arm or host-model scheduling, not determined.
