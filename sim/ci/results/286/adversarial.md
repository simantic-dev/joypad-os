# PR 286 adversarial: Switch 2 Pro init (failed bulk transfer, long config descriptor)

Binary: sim-main, native host, remapper B (main 9fa79f45 vs ci-pr-286 25f48b85). Script `scenarios/adv/286_adv.sh`, options in `scenarios/peers/usb_sw2.py` (`OPT`). Logs `results/286/adv/<opt>.<main|286>.*`.

| # | Attack | main | PR 286 |
|---|---|---|---|
| 1 | baseline 281-byte config, all bulk commands ok | `Invalid config descriptor length: 281`, no bulk endpoint, no init | finds interface 1 and bulk 0x02, 18/18 commands sent |
| 2 | bulk command #3 onward NAKed forever (hung pipe) | no init (same reason as 1) | cmd 3 sent, then **stuck for the rest of the run: 4236 NAK retries, init never completes, no retry/abandon log** |
| 3 | interface 1 placed after 20 alt-settings of interface 0 (config 377 B, interface 1 starts past byte 256) | `Invalid config descriptor length: 377` | `reading first 256` then `No bulk OUT endpoint found on interface 1`, rumble/LED disabled |
| 4 | 4 zero bytes appended inside wTotalLength (bLength 0) | rejected as 285 B | init OK (the zero-length guard is never reached because the endpoint is found first) |
| 5 | bulk command #3 STALL on every command (native host) | no init | cmd 3 sent, then no completion callback and no further command (see simulator note) |

## Findings
**PR-INCOMPLETE (medium): a hung bulk pipe still wedges init.** The PR makes a *failed* transfer clear `xfer_pending` and retry 3 times, but a transfer that never completes (device NAKs bulk OUT forever, or a lost callback) leaves `xfer_pending` set and `task_switch2_pro` returns at `if (inst->xfer_pending) return;` indefinitely; there is no timeout. Repro: `OPT=nak` -> `results/286/adv/nak.286.peer.log` (`BULK OUT #4236 NAK`) and `nak.286.console.txt` (last line `Sending cmd 3/18: 0x16`). Fix: record `platform_time_ms()` when `xfer_pending` is set and treat >N ms as `xfer_failed` (and `tuh_edpt_abort_xfer`).
**PR-INCOMPLETE (low): interface 1 beyond byte 256 is not found.** The PR's own comment says interface 1 "may still be in what we got"; if it is not, init is skipped silently-ish. Fix: fetch `wTotalLength` in a larger buffer or walk with chunked `tuh_descriptor_get_configuration_sync` reads. Repro: `OPT=late1`.
Attack 5: not conclusive. On the native RP2040 host a STALLed bulk OUT is never reported to the callback in the sim, so the retry path cannot be exercised there; the earlier PIO-USB run (results/286/review.md) shows retry works. Possible simulator bug (RP2040 host STALL on bulk OUT), see SUMMARY.
Not run: the PIO-USB failed-bulk retry again (needs the sim-main-inover binary and a PIO build; no time).
