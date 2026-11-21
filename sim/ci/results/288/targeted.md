# PR 288 targeted: router gives a mouse a player slot on movement in simple mode
Verdict: FIX DEMONSTRATED.

Scenario: scenarios/run_host.sh mouse 0x046d 0xc077 <B elf> ... : remapper B (router mode SIMPLE, console: "[ROUTER]  Mode: SIMPLE") with a
scripted HID boot mouse on the native host port (peers/usb_mouse.py): 25 movement reports with no buttons, then a left click, then release.
host_peer.py decodes the EVENTs B ships on the UART link.
main (9fa79f45): "Player 1 assigned: HID Mouse" at 0.7658 s (the click); first EVENT on the link is buttons=0x00001; the 25 movement reports are dropped (38 EVENTs).
PR (c9d1fe90):   "Player 1 assigned: HID Mouse" at 0.6658 s (first movement); 25 buttons=0 EVENTs precede the click (63 EVENTs).
Evidence: results/288/targeted/mouse.{main,288}.{console,link}.txt
