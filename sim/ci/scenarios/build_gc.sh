#!/bin/bash
# build_gc.sh <ref> -> scn/elf/gc_<ref>.elf  (joypad_ngc_rp2040zero = usb2gc_rp2040zero, lane b, build/lane-b/rp)
set -e
REF="$1"; C="$HOME/ahnaf/joypad-ci"; WT="$C/wt/lane-b"; B="$C/build/lane-b"
export PICO_TOOLCHAIN_PATH="$HOME/toolchains/arm/arm-none-eabi" PATH="$HOME/toolchains/arm/bin:$PATH" PICOTOOL_FETCH_FROM_GIT_PATH="$HOME/.picotool"
cd "$C/repo"; if [ "$REF" = main ]; then COMMIT=$(git rev-parse upstream/main); else COMMIT=$(git rev-parse ci-pr-$REF); fi
cd "$WT"; git checkout -q --force --detach "$COMMIT"; git clean -q -fd
git submodule update -q --init --depth 1 src/lib/tinyusb src/lib/tusb_xinput src/lib/libxsm3 src/lib/pico-sdk src/lib/Pico-PIO-USB src/lib/SNESpad src/lib/joybus-pio src/lib/jvsio >/dev/null 2>&1 || true
git -C src/lib/pico-sdk submodule update -q --init lib/btstack >/dev/null 2>&1 || true
export PICO_SDK_PATH="$WT/src/lib/pico-sdk" PICO_TINYUSB_PATH="$WT/src/lib/tinyusb"
[ -f "$B/rp/CMakeCache.txt" ] || cmake -G "Unix Makefiles" -DFAMILY=rp2040 -DPICO_BOARD=pico -DCMAKE_PROJECT_INCLUDE="$C/ps5default.cmake" -S src -B "$B/rp" >/dev/null
(cd "$B/rp" && make joypad_ngc_rp2040zero -j4) > "$C/scn/buildgc_$REF.log" 2>&1
cp "$B/rp/joypad_ngc_rp2040zero.elf" "$C/scn/elf/gc_$REF.elf"; echo ok $REF
