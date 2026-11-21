#!/bin/bash
# build_pio.sh <ref>   usb2usb RP2040 build with PIO-USB host (Feather RP2040, D+=GP16 D-=GP17) + native USB device, default Switch output. prints the elf
. "$HOME/ahnaf/joypad-ci/scenarios/common.sh"
checkout_ref "$1" >&2 || exit 1
build_rp rp_pio joypad_usb_feather_rp2040 "$C/scenarios/switchdefault.cmake" >&2 || exit 1
cp "$B/rp_pio/joypad_usb_feather_rp2040.elf" "/tmp/ja/pio_$REF.elf"; echo "/tmp/ja/pio_$REF.elf"
