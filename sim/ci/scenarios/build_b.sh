#!/bin/bash
# build_b.sh <ref>  -> builds remapper B (native USB host + UART link) for that ref, prints the elf copy's path
. "$HOME/ahnaf/joypad-ci/scenarios/common.sh"
checkout_ref "$1" >&2 && build_rp rpb joypad_usb2usb_remapper_v7_b "$C/scenarios/none.cmake" >&2 || exit 1
mkdir -p /tmp/ja; cp "$B/rpb/joypad_usb2usb_remapper_v7_b.elf" "/tmp/ja/b_$1.elf"; echo "/tmp/ja/b_$1.elf"
