#!/bin/bash
# build_nrf.sh <ref: main|N> [target: bt2usb_feather] -> scn/elf/nrf_<ref>.elf   (lane b only; reuses pr_check.sh's lane-b worktree/build tree)
set -e
REF="$1"; C="$HOME/ahnaf/joypad-ci"; WT="$C/wt/lane-b"; B="$C/build/lane-b"
export PICO_TOOLCHAIN_PATH="$HOME/toolchains/arm/arm-none-eabi" PATH="$HOME/toolchains/arm/bin:$PATH"
cd "$C/repo"; if [ "$REF" = main ]; then COMMIT=$(git rev-parse upstream/main); else COMMIT=$(git rev-parse ci-pr-$REF); fi
cd "$WT"; git checkout -q --force --detach "$COMMIT"; git clean -q -fd
git submodule update -q --init --depth 1 src/lib/tinyusb src/lib/tusb_xinput src/lib/libxsm3 src/lib/pico-sdk >/dev/null 2>&1 || true
git -C src/lib/pico-sdk submodule update -q --init lib/btstack >/dev/null 2>&1 || true
grep -q '^target_compile_options(app PRIVATE -Wno-error=implicit' nrf/CMakeLists.txt || sed -i '' '/^set(TINYUSB_PATH/a\
target_compile_options(app PRIVATE -Wno-error=implicit-function-declaration -Wno-error=int-conversion)  # harness patch (GCC 15)
' nrf/CMakeLists.txt
( . "$HOME/ahnaf/joypad/env.sh"; cd nrf && west build -b adafruit_feather_nrf52840 . -d "$B/nrf" --pristine=auto -- -DAPP_TYPE=bt2usb \
    -DJOYPAD_BOARD=adafruit_feather_nrf52840 -DDTC_OVERLAY_FILE="$PWD/boards/adafruit_feather_nrf52840.overlay" \
    -DEXTRA_CONF_FILE="$PWD/boards/adafruit_feather_nrf52840.conf" ) > "$C/scn/build_$REF.log" 2>&1
cp "$B/nrf/nrf/zephyr/zephyr.elf" "$C/scn/elf/nrf_$REF.elf"; echo "ok $REF"
