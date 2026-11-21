# PR 286 review draft: Switch 2 Pro init survives a long config descriptor and a failed bulk transfer

Verdict: DEMONSTRATED (both halves, the second one on the PIO-USB host only)

## What was tested and how
Firmware: usb2usb remapper B (native RP2040 USB host) and the usb2usb PIO-USB host build (joypad_usb_feather_rp2040), main (9fa79f45) vs the PR (25f48b85, not behind main), in Simantic's RP2040 simulator (USB.PioUsb model for the PIO host). The USB peers are scripted devices built from public descriptor dumps (DS4/DualSense dsremap docs and the dogtopus DualSense gist, report layouts per Linux hid-playstation.c). They are not captures from physical units. Simulator: Simantic's RP2040 simulator (pyrite), a local unreleased build of main plus the PIO-USB host model branches (USB.PioUsb), used for every run below. The Switch 2 Pro peer (057e:2069) is hand-written, not a dump: HID interface 0 (report 0x09), a vendor interface 1 with bulk OUT 0x02 / IN 0x82 and 14 filler alternate settings, so the configuration descriptor is 281 bytes (more than the driver's 256-byte buffer). It ACKs every bulk command (none), STALLs bulk command 3 once (once) or from 3 onwards (always). Script: scenarios/286.sh (native) and scenarios/286_pio.sh (PIO); logs results/286/review/ (native_*, pio_*).

## Results (same on native and PIO unless noted)
- none: main logs "[SWITCH2] Invalid config descriptor length: 281" and "No bulk endpoint - rumble/LED disabled"; device saw 0 bulk OUTs. PR logs "Config descriptor is 281 bytes, reading first 256", "Found bulk OUT endpoint: 0x02", commands 1/18 to 18/18, "Init sequence 1 complete"; device saw 18 bulk OUTs.
- once (PIO): main as none (0 bulk OUTs, so nothing to retry). PR: command 3 STALLs, "Cmd 3 failed, retrying", command 3 ACKed, commands to 18/18, "Init sequence 1 complete"; 19 bulk OUTs.
- always (PIO): PR retries command 3 three times (5 bulk OUTs: 2 ok, 3 STALL) and logs "Cmd 3 failed 3 times, abandoning init", then sends nothing more.
- Native host with once/always: the PR gets as far as command 3 (3 bulk OUTs, 1 STALL) and then nothing further; no "Cmd 3 failed" line. The simulated native host never calls the driver's completion callback on a STALLed bulk endpoint (TinyUSB hcd_rp2040 handles the STALL interrupt only for EPx, so a bulk slot's STALL is not reported). The PR's retry therefore cannot be reached on that host; it is reached on the PIO host.
Both halves match the earlier verdict.

## Bugs or regressions
None attributable to the PR. Observation, same on both refs: "[SWITCH2] Warning: failed to re-request HID report" follows the init sequence.

## Not covered
Real Switch 2 Pro descriptors and command responses (bulk IN replies are not modelled), timing on a real PIO-USB host, the native-host STALL behaviour on silicon.
