#!/usr/bin/env python3
"""Renders docs/images/key_insights_preview.png from data/processed (matplotlib).
This is a PREVIEW of the story the Power BI report tells - it is not a Power BI screenshot."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
f = pd.read_csv(ROOT / "data/processed/fact_survey.csv")
h = pd.read_csv(ROOT / "data/processed/fact_happiness.csv")
MIN_N = 10
BG, PANEL, TXT, MUTED = "#0F1B26", "#16293A", "#E8EEF2", "#B7C4CE"
TEAL, AMBER, RED = "#00A6A6", "#F2B134", "#ED553B"

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": TXT, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(2, 2, figsize=(15, 9), facecolor=BG)
for a in ax.flat:
    a.set_facecolor(PANEL)
    for s in a.spines.values():
        s.set_visible(False)
    a.tick_params(length=0)

def hbar(a, s, title, fmt, color=TEAL, highlight=None):
    s = s.sort_values()
    cols = [AMBER if (highlight and i == highlight) else color for i in s.index]
    a.barh(s.index, s.values, color=cols, height=0.62)
    for y, v in enumerate(s.values):
        a.text(v, y, "  " + fmt(v), va="center", fontsize=9, color=TXT)
    a.set_title(title, loc="left", fontsize=12, fontweight="bold", color=TXT, pad=10)
    a.set_xticks([])
    a.margins(x=0.18)

g = f.groupby("Job Title")["Salary Midpoint"].agg(["mean", "count"])
hbar(ax[0, 0], g[g["count"] >= MIN_N]["mean"], f"Avg salary by role (n >= {MIN_N})", lambda v: f"${v/1000:,.0f}k")

g = f.groupby("Country")["Salary Midpoint"].agg(["mean", "count"])
hbar(ax[0, 1], g[g["count"] >= MIN_N]["mean"], f"Avg salary by country (n >= {MIN_N})", lambda v: f"${v/1000:,.0f}k", color="#3E7CB1")

hs = h.groupby("Happiness Factor")["Happiness Score"].mean()
hbar(ax[1, 0], hs, "Avg happiness by factor (0-10)", lambda v: f"{v:.2f}", color=TEAL, highlight=hs.idxmin())

p = f["Top Job Priority"].value_counts(normalize=True)
p = p[p >= 0.02]
hbar(ax[1, 1], p, "Most important thing in a new job", lambda v: f"{v*100:.0f}%", color="#7FB069")

fig.suptitle("Data Professional Survey - key insights  (n = 630)", x=0.02, ha="left",
             fontsize=17, fontweight="bold", color=TXT)
fig.text(0.02, 0.005, "Preview rendered with matplotlib from data/processed - not a Power BI screenshot. "
         "Salary = band midpoint estimate. Self-selected sample.", fontsize=8.5, color=MUTED)
fig.tight_layout(rect=[0, 0.02, 1, 0.95])
out = ROOT / "docs/images/key_insights_preview.png"
fig.savefig(out, dpi=130, facecolor=BG)
print("wrote", out)
