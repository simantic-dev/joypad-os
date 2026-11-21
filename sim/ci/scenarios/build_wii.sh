#!/bin/bash
# build_wii.sh <ref>  -> builds usb2wiiext_pico (PR 226 target: native USB host -> Wii extension I2C slave) for that ref, prints the elf copy's path
. "$HOME/ahnaf/joypad-ci/scenarios/common.sh"
checkout_ref "$1" >&2 && build_rp rp_wii joypad_usb2wiiext_pico "$C/scenarios/none.cmake" >&2 || exit 1
mkdir -p /tmp/ja; cp "$B/rp_wii/joypad_usb2wiiext_pico.elf" "/tmp/ja/wii_$1.elf"; echo "/tmp/ja/wii_$1.elf"
