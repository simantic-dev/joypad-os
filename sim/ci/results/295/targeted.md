# PR 295 targeted: autofire timing state survives profile_apply
Verdict: DIFFERENCE OBSERVABLE in autofire timing regularity (2026-11-19 rerun, no noled, WS2812 build): main drops/doubles autofire edges, PR is regular. Earlier 'no difference' note below is superseded.

Scenario: scenarios/run_a.sh switch autofire <A elf> (scenarios/295.sh): remapper A in Switch mode (switchdefault.cmake). a_peer.py sends over the
uart_peer link: SELECT+B3 held 2.1 s (runtime-profile gesture -> "Rapid-fire set"), tap B1 (cycles B1 to 30 Hz), tap SELECT (done), then holds B1 for 1 s,
and decodes the Switch HID report. This reaches apply_usbd_profile_player() -> profile_apply() with a stack profile_out, the exact code the PR changes in usbd.c.
Harness patch (both refs, scenarios/build_a.sh noled): leds_is_indicating() never turns false after the gesture's LED indication in the sim build
(cause not isolated), which froze the gesture; the patch drops that one condition from runtime_profile_check_combo().
main (9fa79f45): B1 held 4.9-5.9 s -> 27 presses, press-to-press 24/32/40 ms (33 ms period quantised to the 8 ms feed tick), i.e. 30 Hz autofire works.
PR (b0b870fc):   29 presses, 32/40 ms, same.
Reading: profile_out is a fresh stack variable on every call, yet autofire_start_ms survives on main because the compiler reuses the same stack slot
every call. The PR makes this defined (per-player static) but the output is identical here. A difference would need another call clobbering that stack slot
or per-player interleaving that this UART/merge path does not produce (merge mode folds all UART players into one output).
The native-device changes of the PR (3DO, GameCube, Loopy, N64, Nuon) are not reachable on RP2040 usb2usb.
Evidence: results/295/targeted/af.{main,pr}.{reports,console}.txt


## 2026-11-19 update (lane b, sim = pyrite main + #3853/#3854)
1. RAM power-up fill: pyrite#3854 adds `sram:` overlay keys `ramInit: random`, `ramSeed: N`. Run with it (ram.{main,295}.*): the fill alone does NOT make main misbehave.
   Hold window (B1 held from 4.96 s), press-to-press gaps: main 16/24/32/40 ms (33 presses), PR 32/40 ms (32). Autofire still works because profile_out's
   stack slot is re-written by the same call chain before the next read; random SRAM only changes the first call's start time. What exposes it is another call at the same stack depth.
2. noled removed. Root cause of the stuck leds_is_indicating(): the harness builds PICO_BOARD=pico, which has no PICO_DEFAULT_WS2812_PIN, so ws2812.h defines CONFIG_NO_NEOPIXEL and
   neopixel_task() returns at once, but neopixel_indicate_profile() still sets neopixel_state = BLINK_OFF, which nothing ever clears. Firmware behaviour, identical on silicon with a
   NeoPixel-less board; not a pyrite bug. scenarios/295.sh now builds `switchws` (switchwsdefault.cmake: WS2812_PIN=16, PIO0 ws2812 program runs in pyrite; the gesture completes with no patch).
3. Result with a live LED driver (ws.{main,295}.*): main hold-window presses 22, gaps 24/32/40/56/64/96/104 ms (autofire phase lost); PR 32 presses, gaps 32/40 ms. With the LED driver running
   (neopixel_task/put_pixel in the same loop) the stack slot is clobbered between calls on main, exactly the failure mode of the PR's per-player static. PR regresses nothing.
   Earlier noled runs (af.*) already hinted at it: main gaps 16..72 ms vs PR 32/40.
