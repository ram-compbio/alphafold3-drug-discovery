#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path

INPUT_FILE = "outputs/1_merge_error_bars.tsv"
OUTDIR = "outputs"
ORDER = ["Chain-pair ipTM", "ipTM", "pTM", "Ranking Score"]
COLORS = {"Chain-pair ipTM":"#009E73", "ipTM":"#56B4E9", "pTM":"#CC79A7", "Ranking Score":"#E69F00"}
CONTROL_COLOR = "#C7C7C7"
METRICS = [
    ("nAIA", "nAIA_SEM", "nAIA", "a"),
    ("NDCG", "NDCG_SEM", "NDCG", "b"),
    ("AIA", "AIA_SEM", "AIA", "c"),
    ("AI-NDCG", "AI-NDCG_SEM", "AI-NDCG", "d"),
]

def fmt(v):
    return f"{v:.2f}" if v >= 1 else f"{v:.3f}".rstrip("0").rstrip(".")

def rounded_bar(ax, x, h, w, c, ry):
    l, r = x - w/2, x + w/2
    rx, ry = min(w*0.22, w/2), min(ry, h*0.30)
    verts = [(l,0),(l,h-ry),(l,h-ry*0.25),(l+rx*0.25,h),(l+rx,h),(r-rx,h),
             (r-rx*0.25,h),(r,h-ry*0.25),(r,h-ry),(r,0),(l,0),(l,0)]
    codes = [Path.MOVETO,Path.LINETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.LINETO,
             Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.LINETO,Path.LINETO,Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=c, edgecolor="white", linewidth=0.8, zorder=2))

def panel(ax, df, ctrl, metric, sem, ylab, letter):
    x = np.arange(len(df), dtype=float)
    y = df[metric].astype(float).values
    e = df[sem].astype(float).values
    cv, ce = float(ctrl[metric]), float(ctrl[sem])
    w, ry = 0.72, max(y)*0.04

    for xi, yi, name in zip(x, y, df["Matrix"]):
        rounded_bar(ax, xi, yi, w, COLORS[name], ry)

    ax.bar(x, [cv]*len(x), width=w, color=CONTROL_COLOR, edgecolor="white", linewidth=0.8, zorder=3)
    ax.errorbar(x, y, yerr=e, fmt="none", ecolor="#4A4A4A", capsize=3, elinewidth=1, capthick=1, zorder=5)
    ax.errorbar(x, [cv]*len(x), yerr=[ce]*len(x), fmt="none", ecolor="#666666", capsize=2.5, elinewidth=0.95, capthick=0.95, zorder=6)

    for xi, yi in zip(x, y):
        ax.annotate(fmt(yi),
                    xy=(xi, yi),
                    xytext=(5, 5),
                    textcoords="offset points",
                    ha="left",
                    va="center",
                    fontsize=12,
                    color="#202020",
                    zorder=8)

    ax.set_xticks(x)
    ax.set_xticklabels(df["Matrix"], rotation=25, ha="right", fontsize=13)
    ax.set_ylabel(ylab, fontsize=15)
    ax.tick_params(axis="y", labelsize=13)
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.6, len(df)-0.4)
    ax.set_ylim(0, max(np.max(y+e), cv+ce)*1.05)
    ax.grid(False)
    ax.text(-0.12, 1.03, letter, transform=ax.transAxes, fontsize=16, fontweight="bold")

def main():
    script = os.path.splitext(os.path.basename(__file__))[0]
    outdir = os.path.join(OUTDIR, script)
    os.makedirs(outdir, exist_ok=True)

    df = pd.read_csv(INPUT_FILE, sep="\t")
    ctrl = df[df["Matrix"].str.strip().str.lower() == "control"].iloc[0]
    df = df[df["Matrix"].str.strip().str.lower() != "control"].copy()
    df["Matrix"] = pd.Categorical(df["Matrix"], categories=ORDER, ordered=True)
    df = df.sort_values("Matrix").reset_index(drop=True)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.ravel()

    for ax, (m, s, ylab, letter) in zip(axes, METRICS):
        panel(ax, df, ctrl, m, s, ylab, letter)

    fig.tight_layout()
    png = os.path.join(outdir, "Fig1S_AF3_metrics_evaluation.png")
    fig.savefig(png, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Saved:", png)


if __name__ == "__main__":
    main()