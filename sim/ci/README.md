# Joypad OS in simulation: peers, scenarios, PR results

Stock Joypad OS firmware runs on a simulated RP2040 or nRF52840. Everything off-chip is a scripted Python peer.
Each run script takes `SIM=<path to the sim binary>`.

## Device peers (the controller end)

| File | What it is |
|---|---|
| `scenarios/peers/usb_ds4.py` | DualShock 4: real descriptors (`peers/gen/ds4_*.hex`), scripted button timeline |
| `scenarios/peers/usb_ds5.py` | DualSense: real descriptors (`peers/gen/ds5_*.hex`) |
| `scenarios/peers/usb_sw2.py` | Switch 2 Pro: HID plus a vendor bulk interface; bulk STALL modes; config descriptor over 256 bytes |
| `scenarios/peers/usb_mouse.py` | HID boot mouse |
| `scenarios/peers/usb_combo.py` | Composite mouse + gamepad (idle mouse chatter modes) |
| `scenarios/peers/usb_head.py` | Shared USB device base (enumeration, time-based phases) |
| `../peers/ble_pad.py`, `../nrf_ble.yaml` | BLE HID-over-GATT gamepad on the BLE medium (bt2usb input) |
| `../xbox_rumble_adv.py` | Xbox pad that answers rumble writes late (stop-report loss) |

## Console and host peers (the output end)

| File | What it is |
|---|---|
| `scenarios/peers/wii_master.py` | Wii console: I2C master on the extension port (usb2wii) |
| `../nrf_ble_host.py`, `../peer.py` | USB console host: reads the HID reports Joypad emits |
| `scenarios/host_peer.py`, `scenarios/a_peer.py` | Remapper A/B UART link decoder and driver |

## Run scripts

- `scenarios/run_pio.sh <ds4|ds5|sw2|mouse> <vid> <pid> <elf> <out> [s]`: RP2040 usb2usb with the Pico-PIO-USB host on GP16/17. The PIO program runs cycle by cycle.
- `scenarios/run_host.sh`, `run_a.sh`, `run_wii.sh`, `nrf_cdc.sh`: native-host, remapper, Wii and nRF CDC runs.
- `scenarios/build_*.sh`: build recipes; their paths are the author's layout, so adjust them.
- `scenarios/<PR>.sh`: one scenario per upstream PR. `scenarios/adv/<PR>_adv.sh`: adversarial attacks on that PR.

## Results

- `results/SUMMARY.md`: the PR-by-PR verdicts.
- `results/<PR>/review.md`, `targeted.md`, `adversarial.md`: per PR.
- `results/pio_usb/`: PIO-USB traces and the accuracy report.
