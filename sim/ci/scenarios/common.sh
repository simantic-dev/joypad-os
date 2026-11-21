# Shared helpers for targeted per-PR scenarios (lane a only). Source me; needs C, REF, OUT.
C="$HOME/ahnaf/joypad-ci"; LANE=a; WT="$C/wt/lane-a"; B="$C/build/lane-a"; REPO="$C/repo"
SIM="${SIM:-$HOME/ahnaf/public-demos/bin/sim-0.10.5}"
export PICO_TOOLCHAIN_PATH="$HOME/toolchains/arm/arm-none-eabi" PATH="$HOME/toolchains/arm/bin:$PATH"
export PICOTOOL_FETCH_FROM_GIT_PATH="$HOME/.picotool"

checkout_ref() {  # same steps as pr_check.sh, no builds
  REF="$1"; OUT="$C/results/$REF"; mkdir -p "$OUT"
  [ "$(df -g /System/Volumes/Data | awk 'NR==2{print $4}')" -lt 30 ] && { echo "disk low"; return 1; }
  cd "$REPO" || return 1
  git config protocol.file.allow always
  for m in tinyusb tusb_xinput libxsm3 pico-sdk; do git config submodule.src/lib/$m.url "$HOME/ahnaf/joypad/joypad-os/.git/modules/src/lib/$m"; done
  if [ "$REF" = main ]; then git fetch -q upstream main && COMMIT=$(git rev-parse upstream/main)
  elif [[ "$REF" == *m ]]; then COMMIT=$(git rev-parse "ci-pr-$REF")   # local merge of a PR onto current main (PR 203 is 379 commits behind), branch made by hand
  else git fetch -q upstream "pull/$REF/head:ci-pr-$REF" --force && COMMIT=$(git rev-parse "ci-pr-$REF"); fi || return 1
  cd "$WT" && OLD=$(git rev-parse HEAD) && git checkout -q --force --detach "$COMMIT" && git clean -q -fd -e sim || return 1
  git diff --name-only "$OLD" HEAD | while read f; do [ -f "$f" ] && touch "$f"; done   # make must see every file the switch changed
  git submodule sync -q >/dev/null 2>&1
  git submodule update -q --init --depth 1 src/lib/tinyusb src/lib/tusb_xinput src/lib/libxsm3 src/lib/pico-sdk \
    src/lib/Pico-PIO-USB src/lib/SNESpad src/lib/joybus-pio src/lib/jvsio >/dev/null 2>&1
  git -C src/lib/pico-sdk submodule update -q --init lib/btstack >/dev/null 2>&1
  export PICO_SDK_PATH="$WT/src/lib/pico-sdk" PICO_TINYUSB_PATH="$WT/src/lib/tinyusb"
  echo "checked out $REF = $COMMIT"
}

build_rp() {  # build_rp <dir> <make target> <project-include cmake>
  local d="$B/$1"
  [ -f "$d/CMakeCache.txt" ] || cmake -G "Unix Makefiles" -DFAMILY=rp2040 -DPICO_BOARD=pico -DCMAKE_PROJECT_INCLUDE="$3" -S "$WT/src" -B "$d" >> "$OUT/build.targeted.log" 2>&1
  (cd "$d" && make "$2" -j4) >> "$OUT/build.targeted.log" 2>&1 || { echo "build $1 failed"; tail -5 "$OUT/build.targeted.log"; return 1; }
  echo "$d/$2.elf"
}

build_a() {  # build_a <ps3|switch> -> prints a copy of the elf at /tmp/ja/a_<mode>_<ref>.elf
  build_rp "rp_$1" joypad_usb2usb_remapper_v7_a "$C/scenarios/$1default.cmake" >&2 || return 1
  cp "$B/rp_$1/joypad_usb2usb_remapper_v7_a.elf" "/tmp/ja/a_$1_$REF.elf"; echo "/tmp/ja/a_$1_$REF.elf"
}
