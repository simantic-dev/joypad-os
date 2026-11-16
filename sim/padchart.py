#!/usr/bin/env python3
"""Pad HOME presses sent by peer.py vs HID IN reports seen by the console host. usage: padchart.py <mode> <out.png>"""
import re, sys, csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
mode = sys.argv[1]
presses = [(int(m[1]), m[2]) for l in open(f"out/{mode}.peer.txt") if (m := re.match(r"\s*t=\s*(\d+) ms  pad: HOME (press|release)", l))]
reports = [int(r["t_ms"]) for r in csv.DictReader(open(f"out/{mode}.reports.csv"))]
fig, ax = plt.subplots(figsize=(10, 3))
for t, k in presses: ax.axvline(t, color="#1f6feb" if k == "press" else "#8b949e", lw=1.5)
ax.plot(reports, [1] * len(reports), "r|", ms=20, label=f"HID IN reports seen: {len(reports)}")
ax.plot([], [], color="#1f6feb", label="pad HOME press (blue) / release (grey) sent over UART")
ax.set_yticks([]); ax.set_xlabel("ms of A's clock (8 ms STATUS ticks)"); ax.legend(loc="upper right", fontsize=8)
ax.set_title(f"mode={mode}: gamepad events in, HID reports out (sim 0.10.0, RP2040)")
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=110)
