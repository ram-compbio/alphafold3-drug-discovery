#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import textwrap
import os
from pathlib import Path
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch
from matplotlib import transforms

input_dir = "outputs/5_compare_individual_accuracies"
base_name = os.path.splitext(os.path.basename(__file__))[0]
output_dir = f'../outputs/{base_name}'
os.system(f"rm -rf {output_dir}")
os.makedirs(output_dir, exist_ok=True)

def make_label(row, width=34):
    label = f"{row['DISEASE']} ({int(row['cmpds'])})"
    return "\n".join(textwrap.wrap(label, width=width, break_long_words=False, break_on_hyphens=False))


def rounded_outer_bar(ax, y_center, value, height, radius, color):
    y0 = y_center - height / 2
    y1 = y_center + height / 2
    if value > 0:
        x0 = 0
        x1 = value
        rr = min(radius, (x1 - x0) / 2)
        verts = [(x0, y0), (x1 - rr, y0), (x1, y0), (x1, y0 + height / 2), (x1, y1), (x1 - rr, y1), (x0, y1), (x0, y0)]
        codes = [MplPath.MOVETO, MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3, MplPath.CURVE3, MplPath.CURVE3, MplPath.LINETO, MplPath.CLOSEPOLY]
    else:
        x0 = value
        x1 = 0
        rr = min(radius, (x1 - x0) / 2)
        verts = [(x1, y0), (x0 + rr, y0), (x0, y0), (x0, y0 + height / 2), (x0, y1), (x0 + rr, y1), (x1, y1), (x1, y0)]
        codes = [MplPath.MOVETO, MplPath.LINETO, MplPath.CURVE3, MplPath.CURVE3, MplPath.CURVE3, MplPath.CURVE3, MplPath.LINETO, MplPath.CLOSEPOLY]

    patch = PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", zorder=2)
    ax.add_patch(patch)


def create_plot(tsv):
    metric = (tsv.split("_")[1].replace("nAIA", "new indication accuracy")
                               .replace("AIA", "indication accuracy")
                               .replace("nNDCG", "normalized discounted cumulative gain")
                               .replace("aiNDCG", "Average indication normalized discounted cumulative gain"))
    method = tsv.split("_")[0]
    df = pd.read_csv(f'{input_dir}/{tsv}', sep="\t")
    diff_col = f"BANDOCK_{method}-AF3_{method}_Diff"
    plot_df = df[['DISEASE', 'cmpds', diff_col]].dropna().copy()
    plot_df = plot_df.sort_values(diff_col, ascending=False).reset_index(drop=True)
    plot_df["label"] = plot_df.apply(make_label, axis=1)

    # Layout
    row_step = 1.05
    y = np.arange(len(plot_df)) * row_step
    vals = plot_df[diff_col].to_numpy()

    af3_color = "#009E73"
    bandock_color = "#D55E00"

    # Plot style
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12, "xtick.labelsize": 12})
    fig, ax = plt.subplots(figsize=(12.8, 10.2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Axis limits
    xmin = min(-0.29, vals.min() - 0.05)
    xmax = max(0.19, vals.max() + 0.05)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.9, y[-1] + 1.20)

    bar_h = 0.82

    # Dynamic radius
    x_span = xmax - xmin
    radius = x_span * (0.003 / 0.48)

    # add very faint alternating row guides
    for i, yi in enumerate(y):
        if i % 2 == 0:
            ax.axhspan(yi - row_step/2,
                       yi + row_step/2,
                       color="#FAFAFA",
                       zorder=0)

    # Draw bars
    for yi, v in zip(y, vals):
        color = af3_color if v < 0 else bandock_color
        rounded_outer_bar(ax, yi, v, bar_h, radius=radius, color=color)


    # Zero reference line
    ax.axvline(0, color="#666666", linewidth=0.8, zorder=3)

    for tick in ax.get_yticklabels():
        tick.set_horizontalalignment("right")
        tick.set_multialignment("right")
        tick.set_linespacing(1.3)
        tick.set_clip_on(False)
    ax.tick_params(axis="y", length=0, pad=13)

    # Numeric values inside bars
    base_value_pad = x_span * (0.012 / 0.48)

    for yi, v in zip(y, vals):
        value_pad = min(base_value_pad, abs(v) * 0.20)
        if v < 0:
            # Negative bar: outer end is on the left
            ax.text(v + value_pad, yi, v,
                ha="left",
                va="center",
                fontsize=15,
                color="black",
                fontweight="normal",
                zorder=5)
        else:
            # Positive bar: outer end is on the right
            ax.text(v - value_pad, yi, v,
                ha="right",
                va="center",
                fontsize=15,
                color="black",
                fontweight="normal",
                zorder=5)

    # Direction labels
    top_y = y[-1] + 0.65
    header_trans = transforms.blended_transform_factory(ax.transAxes, ax.transData)

    # Dynamically center each heading within its actual data section
    negative_vals = vals[vals < 0]
    positive_vals = vals[vals > 0]

    if len(negative_vals) > 0:
        af3_x = negative_vals.min() / 2
    else:
        af3_x = xmin / 2

    if len(positive_vals) > 0:
        bandock_x = positive_vals.max() / 2
    else:
        bandock_x = xmax / 2

    fontsize = 15
    ax.text(af3_x, top_y + 0.15, "AF3 higher", ha="center", va="center", color=af3_color, fontsize=fontsize, fontweight="bold")
    ax.text(bandock_x, top_y + 0.15, "BANDOCK+ higher", ha="center", va="center", color=bandock_color, fontsize=fontsize, fontweight="bold")
    ax.text(-0.03, top_y, "Disease (Compounds)", transform=header_trans, ha="right", va="center", fontsize=fontsize, fontweight="bold")
    ax.set_xlabel(f"Differences in {metric}\n(BANDOCK+ {method} − AF3 {method})", fontsize=fontsize, labelpad=fontsize, fontweight="bold")

    # Disease labels
    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["label"], fontsize=fontsize, ha="right", va="center")

    # Clean figure style
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)

    ax.spines["bottom"].set_linewidth(0.8)
    ax.spines["bottom"].set_color("0.35")
    ax.grid(False)
    ax.tick_params(axis="x", width=0.8, length=4, color="0.35")

    # Give long Disease (Compounds) labels enough room
    max_label_len = max(len(line) for label in plot_df["label"] for line in label.split("\n"))
    left_margin = max(0.43, min(0.52, max_label_len * 0.0105))
    plt.subplots_adjust(left=left_margin, right=0.97, top=0.92, bottom=0.105)
    # plt.subplots_adjust(left=left_margin, right=0.97, top=0.99, bottom=0.105)

    png_out = f"{output_dir}/{tsv.replace('.tsv', '.png')}"
    print(f"Saving plot to {png_out}")
    fig.savefig(png_out, dpi=600, bbox_inches="tight")

for tsv in os.listdir(input_dir):
    if not 'comparison' in tsv:
        continue
    try:
        create_plot(tsv)
    except Exception as e:
        print(f"Error processing {tsv}: {e}")

rename_map = {
'pLDDT_nAIA':   'Fig3a_',  'resolution_nAIA':   'Fig3b_',  'unbiased_nAIA':   'Fig3c_',
'pLDDT_NDCG':   'Fig3d_',  'resolution_NDCG':   'Fig3e_',  'unbiased_NDCG':   'Fig3f_',
'pLDDT_AIA':    'Fig3g_',  'resolution_AIA':    'Fig3h_',  'unbiased_AIA':    'Fig3i_',
'pLDDT_AI_NDCG':'Fig3j_',  'resolution_AI_NDCG':'Fig3k_',  'unbiased_AI_NDCG':'Fig3l_'
}

for png in os.listdir(output_dir):
    for key, prefix in rename_map.items():
        if key in png:
            os.rename(os.path.join(output_dir, png), os.path.join(output_dir, prefix + png))
