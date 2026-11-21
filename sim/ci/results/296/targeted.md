# PR 296 targeted: Switch mode SELECT+START -> Capture
Verdict: FEATURE DEMONSTRATED.

Scenario: scenarios/run_a.sh switch capture <A elf>: remapper A built with USBD_DEFAULT_MODE=USB_OUTPUT_MODE_SWITCH (scenarios/switchdefault.cmake),
enumerates as 0f0d:0092; a_peer.py sends SELECT, START, SELECT+START, each 320 ms, and decodes the Switch HID report buttons.
main: SELECT -> 0x0100 [MINUS]; START -> 0x0200 [PLUS]; SELECT+START -> 0x0300 [MINUS+PLUS]
PR:   SELECT -> 0x0100 [MINUS]; START -> 0x0200 [PLUS]; SELECT+START -> 0x2000 [CAPTURE] (Minus/Plus dropped); single presses unchanged.
Not covered: hold-for-video-clip timing (the report just follows the hold).
Evidence: results/296/targeted/capture.{main,pr}.reports.txt
