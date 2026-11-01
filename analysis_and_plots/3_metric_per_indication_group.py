#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
import re

def flatten_results(canbench_folder, prefix=''):
    dfs = []

    for canbenchmark in os.listdir(canbench_folder):
        bench_path = os.path.join(canbench_folder, canbenchmark)
        results_dir = os.path.join(bench_path, "scripts/results_analysed_named")

        for file in os.listdir(results_dir):
            
            if canbench_folder.endswith('old') and 'ndcg' in file:
                continue
            file_path = os.path.join(results_dir, file)
            # print(file_path)
            df = pd.read_csv(file_path, sep='\t')
            df = df.iloc[:, [0, 2]]

            file = file.replace('ndcg', 'nNDCG') if 'associated' in file else file.replace('ndcg', 'ai-ndcg')
            suffix = (file.replace('results_analysed_named', '')
                          .replace('associated', '')
                          .replace('.tsv', '')
                          .replace('-10', ''))
            suffix = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', suffix)
            top10_name =  f"{prefix}_Top10_{suffix}" if prefix else  f"Top10_{suffix}"
            df.columns = ["MESH_ID", top10_name]
            dfs.append(df)

    merged = dfs[0]
    for d in dfs[1:]:
        merged = merged.merge(d, on="MESH_ID", how="outer")

    return merged

mesh_ids = 'MESH_IDs_grouped.tsv'
new = 'af3/interactions/canbenchmarks/new'
old = 'af3/interactions/canbenchmarks/old'

df = pd.read_csv(mesh_ids, sep='\t')
df = df.merge(flatten_results(new, "new"), on="MESH_ID", how="left")
df = df.merge(flatten_results(old, "old"), on="MESH_ID", how="left")


base_name = os.path.splitext(os.path.basename(__file__))[0]
output_dir = f'../outputs/{base_name}'
os.makedirs(output_dir, exist_ok=True)
df.to_csv(f'{output_dir}/{base_name}.tsv', sep='\t', index=False)

# ------------------------------------------------------

def build_df(df, base_cols, selected_cols):
    out = df[base_cols + selected_cols].copy()

    out.columns = (out.columns.str.replace('old', '')
                              .str.replace('new', '')
                              .str.replace('af3_', '')
                              .str.replace('_Top10_', '')
                              .str.replace('__', '_'))
    return out

def mean_by_category(df):
    df = df.drop(columns=["MESH_ID", "Disease"], errors="ignore")
    out = df.groupby(["CATEGORY", "GROUP"], as_index=False).mean().round(4)
    out["control"] = out.filter(regex=r"random[_ -]?(0|1|2)$").mean(axis=1).round(4)
    return out.drop(columns=["bandock"] + out.filter(regex=r"random[_ -]?(0|1|2)$").columns.tolist(), errors="ignore")
    # return df.groupby(["CATEGORY", "GROUP"], as_index=False).mean().round(3)

base_cols = df.columns[:4].tolist()
other_cols = [c for c in df.columns[4:]
                    if 'chain_pair' not in c
                    and 'ranking_score' not in c
                    and '_ptm' not in c]
    
old_cols = [c for c in other_cols if 'old' in c]
nndcg_cols = [c for c in other_cols if 'new' in c and 'nNDCG' in c]
aindcg_cols = [c for c in other_cols if 'new' in c and 'ai-ndcg' in c]

used_cols = set(old_cols + nndcg_cols + aindcg_cols)
rest_cols = [c for c in other_cols if c not in used_cols]

df_old = df[base_cols + old_cols]
df_nndcg = df[base_cols + nndcg_cols]
df_aindcg = df[base_cols + aindcg_cols]
df_rest = df[base_cols + rest_cols]

df_old    = mean_by_category(build_df(df, base_cols, old_cols))
df_nndcg  = mean_by_category(build_df(df, base_cols, nndcg_cols))
df_aindcg = mean_by_category(build_df(df, base_cols, aindcg_cols))
df_rest   = mean_by_category(build_df(df, base_cols, rest_cols))

df_old.to_csv(f'{output_dir}/{base_name}_aia.tsv', sep='\t', index=False)
df_nndcg.to_csv(f'{output_dir}/{base_name}_nNDCG.tsv', sep='\t', index=False)
df_aindcg.to_csv(f'{output_dir}/{base_name}_ai-ndcg.tsv', sep='\t', index=False)
df_rest.to_csv(f'{output_dir}/{base_name}_nAIA.tsv', sep='\t', index=False)