#!/usr/bin/env python3
"""Console timeline PNG from a sim --ascii console log: one tick per log line, grouped by tag.
usage: timeline.py <console.txt> <out.png> <title>"""
import re, sys, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = []
for l in open(sys.argv[1]):
    m = re.match(r"\[([\d.]+)s\] \((\w+)\) (.*)", l)
    if m and m[3].strip() and not set(m[3].strip()) <= {"."}:
        rows.append((float(m[1]), m[3].strip()))
fig, ax = plt.subplots(figsize=(11, max(4, 0.28 * len(rows) + 1.2)))
for i, (t, s) in enumerate(rows):
    ax.plot(t, -i, "o", color="#1f6feb", ms=4)
    ax.text(t + 0.01, -i, s[:90], va="center", fontsize=8, family="monospace")
ax.set_yticks([]); ax.set_xlabel("virtual time (s)"); ax.set_title(sys.argv[3])
ax.set_xlim(0, max(t for t, _ in rows) * 2.2 + 0.1)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=110)
