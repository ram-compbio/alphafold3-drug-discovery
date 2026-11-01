#!/usr/bin/env python3
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, PathPatch
from matplotlib.path import Path
import re

INPUT_FILE = "1_merge_error_bars.tsv"
OUTDIR = "outputs"
TAG_ORDER = ["pLDDT", "Resolution", "Unbiased", "Current", "Full"]
PROGRAM_ORDER = {"BANDOCK+": 0, "AF3": 1, "BANDOCK": 2}
LABEL_ORDER = {"All": 0, "Top": 1, "Bottom": 2, "Current": 3, "Full": 4}
TAG_COLORS = {
    "pLDDT": "#009E73",      # bluish green
    "Resolution": "#E69F00", # orange
    "Unbiased": "#0072B2",   # blue
    "Current": "#CC79A7",    # reddish purple
    "Full": "#D55E00"        # vermillion
}


def get_tag_color(tag):
    tag = str(tag)

    if re.search(r"pLDDT", tag, re.IGNORECASE):
        return TAG_COLORS["pLDDT"]

    if re.search(r"Resolution", tag, re.IGNORECASE):
        return TAG_COLORS["Resolution"]

    if re.search(r"Unbiased", tag, re.IGNORECASE):
        return TAG_COLORS["Unbiased"]

    if re.search(r"Current", tag, re.IGNORECASE):
        return TAG_COLORS["Current"]

    if re.search(r"Full", tag, re.IGNORECASE):
        return TAG_COLORS["Full"]

    return "#808080"   # fallback gray if unknown

DISPLAY_TAG = {"pLDDT": "Based on AF3 pLDDT",
    "Resolution": "Based on PDB Resolution",
    "Unbiased": "Based on Unbiased Set",
    "Current": "Currently completed AF3",
    "Full": "Full CANDO Library"}
    
CONTROL_COLOR = "#B3B3B3"
PROGRAM_BRACKET_COLOR = "#666666"
METRICS = [ ("nAIA", "nAIA_SEM", "Normalized average indication accuracy\n(nAIA)"),
            ("nNDCG", "nNDCG_SEM", "Normalized discounted cumulative gain\n(nDCG)"),
            ("ai-ndcg", "ai-ndcg_SEM", "Average indication normalized discounted cumulative gain\n(AI nDCG)"),
            ("aia", "aia_SEM", "Average indication accuracy\n(AIA)")]

def contiguous_runs(indices):
    if not indices:
        return []

    runs = []
    start = prev = indices[0]
    for i in indices[1:]:
        if i != prev + 1:
            runs.append((start, prev))
            start = i
        prev = i

    runs.append((start, prev))
    return runs

def format_value(metric, value):
    return f"{value:.3f}" if metric in ("nNDCG", "ai-ndcg") else f"{value:.2f}"

def rounded_top_bar(ax, xcenter, height, width, color, radius_y=None, zorder=2):
    left, right, top = xcenter - width / 2, xcenter + width / 2, height

    radius_y = max(height * 0.05, 0.02) if radius_y is None else radius_y
    r_y = min(radius_y, height * 0.30)
    r_x = min(width * 0.22, width / 2)

    verts = [(left, 0),
             (left, top - r_y),
             (left, top - r_y * 0.25),
             (left + r_x * 0.25, top),
             (left + r_x, top),
             (right - r_x, top),
             (right - r_x * 0.25, top),
             (right, top - r_y * 0.25),
             (right, top - r_y),
             (right, 0),
             (left, 0),
             (left, 0)]

    codes = [Path.MOVETO,
             Path.LINETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.LINETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.LINETO,
             Path.LINETO,
             Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor="white", linewidth=0.8, zorder=zorder))


def bracket(ax, x0, x1, y, label, color, lw=2.0, fontsize=11.5, cap=0.022, label_gap=0.018):
    trans = ax.get_xaxis_transform()

    for xs, ys in [([x0, x1], [y, y]), ([x0, x0], [y, y + cap]), ([x1, x1], [y, y + cap])]:
        ax.plot(xs, ys, transform=trans, color=color, lw=lw, solid_capstyle="round", clip_on=False)

    ax.text((x0 + x1) / 2, y - label_gap, label, transform=trans, ha="center", va="top",
            fontsize=fontsize, color="#333333", clip_on=False)

def sort_data(df):
    df = df.copy()
    df["_tag"] = df["Tag"].map(lambda x: TAG_ORDER.index(x) if x in TAG_ORDER else 999)
    df["_program"] = df["Program"].map(lambda x: PROGRAM_ORDER.get(x, 999))
    df["_label"] = df["Label"].map(lambda x: LABEL_ORDER.get(x, 999))
    df["_protein"] = -pd.to_numeric(df["Proteins"], errors="coerce").fillna(0)
    return df.sort_values(["_tag", "_program", "_protein", "_label"]).drop(columns=["_tag", "_program", "_label", "_protein"]).reset_index(drop=True)

def make_plot(df, control_row, metric, sem_col, ylab, out_dir):
    x = np.arange(len(df), dtype=float)
    vals = df[metric].astype(float).values
    errs = df[sem_col].astype(float).values
    control_val = float(control_row[metric])
    control_err = float(control_row[sem_col])

    fig, ax = plt.subplots(figsize=(16, 9.2))

    bar_width = 0.72
    radius_y = max(vals) * 0.04 if len(vals) else 0.1
    rows = df.to_dict("records")

    for xi, row, val in zip(x, rows, vals):
        rounded_top_bar(ax, xi, val, bar_width, get_tag_color(row["Tag"]), radius_y)

    ax.bar(x, [control_val] * len(x), width=bar_width, color=CONTROL_COLOR, edgecolor="white", linewidth=0.8, zorder=3)
    ax.errorbar(x, vals, yerr=errs, fmt="none", ecolor="#4A4A4A", capsize=3, elinewidth=1, capthick=1, zorder=5)
    ax.errorbar(x, [control_val] * len(x), yerr=[control_err] * len(x), fmt="none", ecolor="#666666", capsize=2.5, elinewidth=0.95, capthick=0.95, zorder=6)
    label_gap = max((max(vals) if len(vals) else 1) * 0.025, control_err * 1.5)

    for xi, row, val in zip(x, rows, vals):
        ypos = min(control_val + control_err + label_gap,
            control_val + (val - control_val) * 0.35)

        ax.text(xi, ypos, f'{row["Label"]}',
            ha="center", va="bottom", rotation=90,
            fontsize=10, linespacing=1.5, color="#222222", zorder=7)

    for xi, val in zip(x, vals):
        ax.text(xi + bar_width * 0.10,  # right side of the bar
                val,                         # top of the bar
                format_value(metric, val),
                ha="left",
                va="bottom",
                fontsize=10,
                color="#202020",
                zorder=8)

    ax.set_xticks(x)
    ax.set_xticklabels([""] * len(x))
    ax.tick_params(axis="x", length=0)

    tags = df["Tag"].tolist()

    for i in range(1, len(tags)):
        if tags[i] != tags[i - 1]:
            ax.axvline(i - 0.5, color="#E2E2E2", linewidth=1.2, zorder=0)

    # program brackets
    for tag in TAG_ORDER:
        tag_idx = [i for i, r in enumerate(rows) if r["Tag"] == tag]

        for program in PROGRAM_ORDER:
            idx = [i for i in tag_idx if rows[i]["Program"] == program]
            for start, end in contiguous_runs(idx):
                bracket(ax,
                        start - bar_width / 2,
                        end + bar_width / 2,
                        -0.045,
                        program,
                        PROGRAM_BRACKET_COLOR,
                        lw=1.7,
                        fontsize=10,
                        cap=0.018,
                        label_gap=0.016)

    ax.set_ylabel(ylab, fontsize=11)
    ax.grid(False) #ax.grid(axis="y", alpha=0.15, zorder=0)
    ax.set_xlim(-0.65, len(df) - 0.35)

    _, ymax = ax.get_ylim()
    ax.set_ylim(0, ymax * 1)

    handles = [
    Patch(facecolor=TAG_COLORS[t], label=DISPLAY_TAG.get(t, t))
    for t in TAG_ORDER
    if t in df["Tag"].values]
    handles.append(Patch(facecolor=CONTROL_COLOR, label="Control"))

    ax.legend(handles=handles,
              ncol=len(handles),
              loc="upper center",
              bbox_to_anchor=(0.5, 1.08),
              frameon=False,
              fontsize=11,
              handlelength=1.8,
              columnspacing=1.6)

    fig.subplots_adjust(top=0.82, bottom=0.38, left=0.08, right=0.985)
    out_png = os.path.join(out_dir, metric.replace("-", "_") + ".png")
    fig.savefig(out_png, dpi=260, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Saved:", out_png)

def filter_dataframe(df, keep_column, keep_patterns=None,
                     exclude_column=None, exclude_patterns=None,
                     case=False):

    keep_mask = pd.Series(True, index=df.index)
    exclude_mask = pd.Series(False, index=df.index)

    if keep_patterns:
        keep_mask = df[keep_column].astype(str).str.contains("|".join(keep_patterns), case=case, na=False, regex=True)

    if exclude_patterns:
        exclude_mask = df[exclude_column].astype(str).str.contains("|".join(exclude_patterns), case=case, na=False, regex=True)

    return df[keep_mask & ~exclude_mask]

def main():
    def normalize_tag(tag):
        tag = str(tag)
        for key in TAG_ORDER:
            if re.search(key, tag, re.IGNORECASE):
                return key
        return tag

    script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    out_dir = os.path.join(OUTDIR, script_name)
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(INPUT_FILE, sep="\t")
    df["Tag"] = df["Tag"].apply(normalize_tag)

    if "Matrix" in df.columns and "Program" in df.columns:
        is_matrix_100 = df["Matrix"].astype(str).str.contains("100", case=False, na=False)
        is_control = df["Program"].astype(str).str.contains("control", case=False, na=False)
        df = df[is_matrix_100 | is_control]

    df["Program"] = df["Program"].replace({"BANDOCK+": "BANDOCK"})
    control_mask = df["Program"].astype(str).str.strip().str.lower() == "control"
    control_row = df[control_mask].iloc[0]
    data = sort_data(df[~control_mask].copy())

    for metric, sem_col, label in METRICS:
        make_plot(data, control_row, metric, sem_col, label, out_dir)

if __name__ == "__main__":
    main()