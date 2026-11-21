# PR 279 targeted: don't touch BTstack bonds before BT is started (usb2gc config mode, #278)
Scenario: scenarios/279.sh. usb2gc_rp2040zero (joypad_ngc_rp2040zero, cmake target in lane-b rp tree) on a simulated RP2040 (sim-0.10.5) with no GameCube console -> CDC config mode, BTstack never started (BT.STATUS "enabled":false). USB host (cdc_host.py, binary-framed CDC) sends BT.STATUS, BT.BONDS.CLEAR, PROFILE.LIST.
Main: BT.STATUS answers normally, BT.BONDS.CLEAR returns {"ok":true}, PROFILE.LIST answers. NO hard fault in the sim.
PR: BT.STATUS same, BT.BONDS.CLEAR returns {"ok":false,"error":"bluetooth not running"}, PROFILE.LIST answers.
Verdict: PARTLY DEMONSTRATED. The new guard in BT.BONDS.CLEAR is visible (main runs delete_all_bonds -> start_scan on a NULL hci_stack and says ok; PR refuses). The reported HardFault from BT.STATUS (gap_link_key_iterator_init on NULL hci_stack) did NOT reproduce on main: the NULL-pointer read is harmless in pyrite (reads return data / 0, no bus fault), so the crash and the guard in btstack_host_list_classic_bonds are not distinguishable here. A sim fidelity gap (unmapped/ROM read behaviour), not evidence against the PR.
nRF bt2usb: BT is started at boot there, so the pre-start path does not exist; its checks (13/13) unchanged.
Evidence: results/279/targeted/{main,pr}_host.txt

## 2026-11-19 update: HardFault reproduced
Root cause: BT.STATUS -> btstack_host_list_classic_bonds -> gap_link_key_iterator_init with hci_stack == NULL. `ldr r3,[r3,#20]` reads hci_stack->link_key_db from ROM address 0x14, which on
RP2040 (and pyrite's ROM) is the boot ROM table pointers = 0x1EF01EB0; non-NULL, so `ldr r3,[r3,#24]` loads from 0x1EF01EC8, an unmapped address (datasheet 2.2: unmapped ranges raise a bus error)
-> HardFault at pc 0x10036ff0. So the real crash is a BUS ERROR on a read through a ROM-derived wild pointer, not a NULL read. Pyrite read 0 there (bus map not recorded for RP2040).
Fix: pyrite#3853 (Bus.Reserved for the datasheet's unmapped spans). With it: main HardFaults on BT.STATUS (lockup, no reply, sim.log "FAULT: HardFault ... pc 0x10036ff0 gap_link_key_iterator_init"),
PR #279 answers all three commands. (`--trap-unmapped` on the old sim shows the same.) Writes to ROM are silent on silicon (datasheet 2.8.1), unchanged.
