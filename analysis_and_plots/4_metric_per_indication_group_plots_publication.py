#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.lines import Line2D
from matplotlib.patches import Circle
from PIL import Image

def category_legend(tsv):
    df = pd.read_csv(tsv, sep="\t")

    cat_df = (df[["GROUP", "CATEGORY"]].drop_duplicates().sort_values("CATEGORY"))
    fig, ax = plt.subplots(figsize=(4, 10), dpi=300)
    ax.axis("off")

    y = 1.0
    dy = 0.04
    for _, r in cat_df.iterrows():
        ax.text(0.0, y, f"{r['CATEGORY']} - {r['GROUP']}", fontsize=12, va="top")
        y -= dy

    plt.savefig(category_png, facecolor="white", dpi=300, bbox_inches='tight')
    plt.close()

def stitch_side_by_side(left_png, right_png):
    img_left = Image.open(left_png).convert("RGBA")
    img_right = Image.open(right_png).convert("RGBA")

    h = min(img_left.height, img_right.height)
    if img_left.height != h:
        img_left = img_left.resize((img_left.width, h), Image.LANCZOS)
    if img_right.height != h:
        img_right = img_right.resize((img_right.width, h), Image.LANCZOS)

    stitched = Image.new("RGBA", (img_left.width + img_right.width, h), (255, 255, 255, 255))
    stitched.paste(img_left, (0, 0))
    stitched.paste(img_right, (img_left.width, 0))
    stitched.save(right_png, dpi=(300, 300))


def radar_plot(tsv, matrix):
    
    df = pd.read_csv(tsv, sep="\t")
    categories = df["CATEGORY"].tolist()

    df.columns = df.columns.str.replace("ai-ndcg-", "").str.replace("nNDCG-", "")
    matrix_new = matrix.replace("iptm", "AF3").upper()
    rename = {
        "control": "Control",
        f"{matrix}_all200_plddt": f"200 proteins based on pLDDT scores",
        f"{matrix}_all200_res": f"200 proteins based on PDB resolution",
        f"{matrix}_random200": f"200 unbiased proteins",
    }

    df = df.rename(columns=rename)
    metrics = list(rename.values())

    colors = [
        "#C7C7C7",  # control - gray
        "#009E73",  # pLDDT - bluish green
        "#D55E00",  # resolution - vermillion
        "#56B4E9",  # unbiased - sky blue
    ]

    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
    angles = np.concatenate([angles, [angles[0]]])

    RADIAL_SCALES = {
    "nAIA":    (0, 18, 3),
    "aia":     (0, 40, 10),
    "nNDCG":   (0, 0.12, 0.02),
    "ai-ndcg": (0, 0.08, 0.02)}

    # Fixed radial limits shared by AF3 and BANDOCK+ for each metric
    metric_name = os.path.basename(tsv).replace(".tsv", "").split(
        "3_metric_per_indication_group_")[-1]

    r_min, r_max, r_step = RADIAL_SCALES[metric_name]
    r_ticks = np.arange(r_min, r_max + r_step / 2, r_step)

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    if metric_name in ("nNDCG", "ai-ndcg"):
        ax.set_yticklabels([f"{v:.2f}" for v in r_ticks])
    # Leave space on the RIGHT for legends
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.78, box.height])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.tick_params(axis="x", pad=4)

    ax.set_rlabel_position(160)
    ax.set_ylim(r_min, r_max)
    ax.set_yticks(r_ticks)
    ax.tick_params(axis="y", pad=8, labelsize=12, labelrotation=90)

    ax.spines["polar"].set_color("0.90")
    ax.spines["polar"].set_linewidth(0.95)

    ax.yaxis.grid(False)
    ax.xaxis.grid(True, color="0.30", lw=0.1)
    theta = np.linspace(0, 2*np.pi, 500)

    for i in range(len(r_ticks)-1):
        if i % 2 == 0:
            ax.fill_between(
                theta,
                r_ticks[i],
                r_ticks[i+1],
                color="#FBFBFB",
                zorder=0)

    for i, metric in enumerate(metrics):
        values = df[metric].to_numpy()
        values = np.concatenate([values, [values[0]]])
        ax.plot(angles, values, linewidth=1.5, color=colors[i])

    legend_labels = ["Control", "pLDDT", "Resolution", "Unbiased"]

    for i, label in enumerate(legend_labels):
        y = 0.70 - i * 0.02

        fig.add_artist(Line2D([0.64, 0.67],
                [y + 0.11, y + 0.11],
                transform=fig.transFigure,
                color=colors[i],
                linewidth=2))

        fig.text(0.68,
            y + 0.11,
            label,
            fontsize=12,
            va="center")

    MATRIX_TAG = { "bandockplus": "BANDOCK+", "iptm": "AlphaFold3"}
    matrix_title = MATRIX_TAG.get(matrix, matrix)

    base = os.path.basename(tsv).replace('.tsv', '')
    title_str = (base.split('_')[-1]
                     .replace('nAIA', 'MeSH Group nAIA')
                     .replace('aia', 'MeSH Group AIA')
                     .replace('nNDCG', 'MeSH Group NDCG')
                     .replace('ai-ndcg', 'MeSH Group AI-NDCG'))
    fig.text(0.09,   # left/right position
             0.775,   # height 
             f'{title_str}\n{matrix_title}',
             fontsize=13,
             ha="left",
             va="center")
    fig_name = f"{plot_dir}/{matrix_new}_{title_str.replace(' ', '_').replace('-', '_')}.png"
    plt.savefig(fig_name, facecolor="white", dpi=300, bbox_inches='tight')
    plt.close()

base_name = os.path.splitext(os.path.basename(__file__))[0]
tsv_dir = "../outputs/3_metric_per_indication_group"
plot_dir = f'../outputs/{base_name}'
category_png = f"{plot_dir}/_category_key.png"
nAIA = f"{tsv_dir}/3_metric_per_indication_group_nAIA.tsv"
aia = f"{tsv_dir}/3_metric_per_indication_group_aia.tsv"
nNDCG = f"{tsv_dir}/3_metric_per_indication_group_nNDCG.tsv"
ai_nNDCG = f"{tsv_dir}/3_metric_per_indication_group_ai-ndcg.tsv"

os.system(f"rm -rf {plot_dir}")
os.makedirs(plot_dir, exist_ok=True)
category_legend(nAIA)

for tsv in [nAIA, aia, nNDCG, ai_nNDCG]:
    radar_plot(tsv, 'bandockplus')
    radar_plot(tsv, 'iptm')

for png in os.listdir(plot_dir):
    png_path = os.path.join(plot_dir, png)
    rename_map = {
        ('Group_nAIA',    'AF3'):         'Fig2a_',
        ('Group_nAIA',    'BANDOCKPLUS'): 'Fig2b_',
        ('Group_NDCG',    'AF3'):         'Fig2c_',
        ('Group_NDCG',    'BANDOCKPLUS'): 'Fig2d_',
        ('Group_AIA',     'AF3'):         'Fig2e_',
        ('Group_AIA',     'BANDOCKPLUS'): 'Fig2f_',
        ('Group_AI_NDCG', 'AF3'):         'Fig2g_',
        ('Group_AI_NDCG', 'BANDOCKPLUS'): 'Fig2h_'}

    for (group, model), prefix in rename_map.items():
        if group in png and model in png:
            os.rename(png_path, os.path.join(plot_dir, prefix + png))
