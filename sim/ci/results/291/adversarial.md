# PR 291 adversarial: square sticks in PS3 mode

Offline exhaustive test of the PR's `ps3_stick_circle_to_square` (copied verbatim, compiled with cc, all 65536 inputs; scratch removed). Results: no sign flips, no output closer to centre than the input, monotonic along each axis, saturates correctly (-128,-128), (127,-128), cardinals unchanged, (1,1)->(1,1), (90,90)->(127,127).
Observation (design, low): cross-axis coupling. Holding Y at +64 and sweeping X: output Y goes 64, 65, 71, 80, 90 (at X=64), 82, 77, 73, 72, so a pure X sweep moves the reported Y by up to +26 counts. That is inherent to radial scaling, and a DS3's own gate does not do it, but PS3 games with a deadzone near the axis can feel it. Not a bug; reported for the owner.
Not run: sim of PS3 mode (needs PS3 USB host peer; results/291/targeted covers one diagonal). Findings: none (NONE).
