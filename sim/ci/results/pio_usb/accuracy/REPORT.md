# Pio-USB host + DS4/DualSense accuracy pass, 2026-11-20

Binary for the end-to-end runs: a throwaway local merge (not pushed) of #3875 + new commit, main, #3871, #3873, #3923 built in the `piousb-acc` worktree. Evidence in this directory; "before" files are in `before/`.

## Gap 1: peer descriptors and reports were synthetic
Was: 101-byte hand-made DS4 report descriptor, 32-byte config body, no strings, bInterval 8 (DS4) / 4 (DS5), report built from Joypad's own struct (DS4 had no triggers, no touch count).
Now (`scenarios/peers/usb_ds4.py`, `usb_ds5.py`, `usb_head.py`, `gen/`):
- Device, 225-byte (DS4) / 227-byte (DS5) configuration with the 3 audio interfaces + HID interface 3, EP 0x84/0x03, bInterval 5 (DS4) / 4 (DS5), bcdDevice 0x0100: real 054c:09cc / 054c:0ce6 dumps in dsremap docs (https://dsremap.readthedocs.io/en/latest/reverse.html).
- HID report descriptors: DS4 507 bytes (same page, real dump); DS5 273 bytes, byte-identical in two independent sources (dsremap page and dogtopus gist 894da226d73afb3bdd195df41b3a26aa, compiled by `gen/hidrd2bytes.py`; 273 = the wDescriptorLength in the real config).
- Strings (LANGID 0x0409, manufacturer, product): "Sony Computer Entertainment"/"Wireless Controller", "Sony Interactive Entertainment"/"DualSense Wireless Controller".
- Input reports: 64 bytes laid out per Linux `hid-playstation.c` (`dualshock4_input_report_usb`, `dualsense_input_report`) and the dsremap offset tables; sticks, L2/R2 analog + digital bits, timestamp, gyro/accel, battery, touch count, touch reports; DS5 byte 10 has PS/touchpad/mute in bits 0-2 (clear) with the frame counter in the upper bits.
- Feature reports GET_REPORT DS4 0x02 (37 B), 0xa3 (49 B), 0x12 (16 B); DS5 0x05 (41 B), 0x09 (20 B), 0x20 (64 B): sizes/offsets per hid-playstation.c; values are representative (+-8192 span, 540 speed, a date, a MAC), NOT a dump of one unit.
- Evidence: `gap1_descriptors.txt`, `ds4.after.*`, `ds5.after.*`, `ds5.bridge.*` (mount, "Player 1 assigned", reports).
- Finding: this Joypad build never sends GET_REPORT on these pads (peer log has no GET_REPORT), so the feature replies are served but unexercised.

## Gap 2: DS5 forwarding unproven; sticks/triggers only on DS4
Phases are now time based on the poll clock (1 s each, from 3 s after mount: Cross, left stick up-right, right stick down-left, L2 full, R2 half, touch). Output tap (`--usb-hid-tap usb`, Switch-mode report), identical for DS4 and DS5:
```
3.711 02 00 08 80 80 80 80 00   Cross (B)
5.708 00 00 08 ff 01 80 80 00   left stick right/up
7.708 00 00 08 80 80 01 ff 00   right stick left/down
9.708 40 00 08 80 80 80 80 00   L2 (ZL)
10.708 80 00 08 80 80 80 80 00  R2 half (ZR; Switch output has digital triggers only)
```
Files: `ds4.after.console.txt`, `ds5.after.console.txt`, `ds5.bridge.console.txt`. Router: "Player 1 assigned" on the first button activity (3.70 s now, was 0.8 s because the old peer pressed Cross after 25 polls).

## Gap 3: bridge simplifications (commit 8bc9f54da on #3875 `feat/pio-usb`)
- EP0 MPS: was assumed 64 until a chunk had already been cut at 64, so an MPS-8 device's first descriptor read came back as one 18-byte packet. Now `Downstream::in_token` reads bMaxPacketSize0 from the device descriptor answer and splits at it from the first packet. The existing unit test `control_read_with_data_toggles_and_a_status_stage` only collected bytes; it now asserts packet sizes 8, 8, 2. DS4/DS5 (MPS 64) unchanged.
- `turnaroundNs` default 400 -> 417 (5 full-speed bit times, inside the 2..6.5 bit window of USB 2.0 7.1.19.1; 7.5 at the host with cable). Still an overlay key. An answer later than 18 bit times (the host's 16..18 timeout; `HOST_TIMEOUT_BITS`) is lost: device state advances, nothing is driven, the host's retry meets the 8.6 duplicate rules. Unit test `an_answer_past_the_host_timeout_is_lost_...`. End to end: `ds5.turn2100.console.txt` (0 mounts) vs `ds5.turn1000.console.txt` (mounts, 1000 ns is past 6.5 bits but inside the timeout).
- Toggle/retry/duplicate OUT reviewed against 8.6: SETUP resets both toggles to DATA1, unACKed IN is resent unchanged, mismatched-toggle OUT is ACKed and dropped, NAK leaves the toggle: correct. Not changed.

## Gap 4: 4-byte Thumb instruction across a 64-byte line (#3923)
No bug. `note_code` marks the first and last byte of each instruction in its own line, so a 32-bit instruction at offset 62 marks line L hw 31 and line L+1 hw 0; `halfwords()` is only used for stores and is called per line. Test `store_over_either_half_of_a_line_straddling_instruction_flushes` added on `fix/code-line-halfwords` (commit 8e7b2a8cd, plain push); it passes against unmodified code. Evidence: `gap4.txt`.

## Checks
- Unit tests (`-p engine --lib`: usb, pio_usb, usb_wire, rp2040_pio, machine::): 259 passed.
- `RUSTFLAGS="-D warnings" cargo check -p sim` and `--features cloud-sim`: both pass (cargo check, exit 0).
- `scenarios/286_pio.sh`: NOT run (needs two firmware builds per ref; no time).

## Still not faithful
- Feature report values are representative, not one unit's dump; Joypad does not request them here so they are unexercised. DS5 auth reports (0xF0-0xF2) are in the descriptor but answered STALL.
- No audio endpoints/isochronous; the audio interfaces exist only as descriptors (SET_INTERFACE would be STALLed or ACKed by the generic path).
- Touch report 1 and 2 are always "no finger"; gyro/accel are constants; timestamps count the nominal poll interval, not simulated time.
- Dev-side latency is a constant per run, not per device/packet; a late answer (>18 bits) is dropped rather than appearing on the wire late.
- Single endpoint's unACKed IN slot (`unacked`); two interleaved retrying endpoints would lose one retry.
- bInterval is honoured by the host's poll schedule only as far as TinyUSB/Pico-PIO-USB implement it.
