#!/usr/bin/env python3
import pandas as pd
import os
import re

new_bandock_current = 'af3/interactions/canbenchmarks/new/bandockplus_1103_2449/scripts/results_analysed_named'
old_bandock_current = 'af3/interactions/canbenchmarks/old/bandockplus_1103_2449/scripts/results_analysed_named'
new_af3_current = 'af3/interactions/canbenchmarks/new/iptm_1103_2449/scripts/results_analysed_named'
old_af3_current = 'interactions/canbenchmarks/old/iptm_1103_2449/scripts/results_analysed_named'

nAIA_bandock_current = f'{new_bandock_current}/results_analysed_named-bandockplus_1103_2449-10-associated.tsv'
nNDCG_bandock_current = f'{new_bandock_current}/results_analysed_named-ndcg-bandockplus_1103_2449-10-associated.tsv'
aiNDCG_bandock_current = f'{new_bandock_current}/results_analysed_named_ndcg-bandockplus_1103_2449.tsv'
nAIA_af3_current = f'{new_af3_current}/results_analysed_named-iptm_1103_2449-10-associated.tsv'
nNDCG_af3_current = f'{new_af3_current}/results_analysed_named-ndcg-iptm_1103_2449-10-associated.tsv'
aiNDCG_af3_current = f'{new_af3_current}/results_analysed_named_ndcg-iptm_1103_2449.tsv'

oAIA_bandock_current = f'{old_bandock_current}/results_analysed_named-bandockplus_1103_2449.tsv'
oAIA_af3_current = f'{old_af3_current}/results_analysed_named-iptm_1103_2449.tsv'

results = { 
    'nAIA_BANDOCK_current': nAIA_bandock_current,
    'nNDCG_BANDOCK_current': nNDCG_bandock_current,
    'aiNDCG_BANDOCK_current': aiNDCG_bandock_current,
    'oAIA_BANDOCK_current': oAIA_bandock_current,
    'nAIA_AF3_current': nAIA_af3_current,
    'nNDCG_AF3_current': nNDCG_af3_current,
    'aiNDCG_AF3_current': aiNDCG_af3_current,
    'oAIA_AF3_current': oAIA_af3_current
}

dfs = []
for name, path in results.items():
    matrix = name.replace('_old', '').replace('_new', '')
    cols = pd.read_csv(path, sep='\t', nrows=0).columns
    selected_cols = [cols[0], cols[1], cols[2], cols[-1]]
    df = pd.read_csv(path, sep='\t', usecols=selected_cols, dtype=str)
    df.columns = ['MESH_ID', f'{matrix}_cmpds', matrix, 'DISEASE']
    df = df.set_index(['MESH_ID', 'DISEASE'])
    dfs.append(df)

df_final = pd.concat(dfs, axis=1)
df_final = df_final.reset_index()

cmpd_cols = [c for c in df_final.columns if c.endswith('_cmpds')]
df_final['cmpds'] = pd.to_numeric(df_final[cmpd_cols[0]], errors='coerce')
df_final = df_final.drop(columns=cmpd_cols)

base_name = os.path.splitext(os.path.basename(__file__))[0]
output_dir = f'../outputs/{base_name}'
os.system(f"rm -rf {output_dir}")
os.makedirs(output_dir, exist_ok=True)
df_final.to_csv(f'{output_dir}/{base_name}.tsv', sep='\t', index=False)

base_cols = ['MESH_ID', 'DISEASE', 'cmpds']
df_AIA = df_final[base_cols + [c for c in df_final.columns if re.search(r'(^|_)oAIA_', c)]].copy()
df_nAIA = df_final[base_cols + [c for c in df_final.columns if re.search(r'(^|_)nAIA_', c)]].copy()
df_NDCG = df_final[base_cols + [c for c in df_final.columns if re.search(r'(^|_)nNDCG_', c)]].copy()
df_AINDCG = df_final[base_cols + [c for c in df_final.columns if re.search(r'(^|_)aiNDCG_', c)]].copy()

disease_map = pd.read_csv(f'../outputs/mesh/MESH_shortname_map.tsv', sep='\t')
disease_dict = dict(zip(disease_map["Original"], disease_map["Short"]))

def process_df(df, df_name, ia=30, metric='pLDDT'):
    base = ['MESH_ID', 'DISEASE', 'cmpds']
    metrics = [c for c in df.columns if c not in base]

    df = df.copy()
    df[metrics] = df[metrics].apply(pd.to_numeric, errors='coerce')

    BANDOCK_current = [c for c in metrics if 'BANDOCK' in c][0]
    AF3_current = [c for c in metrics if 'AF3' in c][0]

    df['BANDOCK-AF3_Diff'] = (df[BANDOCK_current] - df[AF3_current])

    diff_cols = ['BANDOCK-AF3_Diff']
    df = df[base + metrics + diff_cols]

    numeric_cols = df.columns.difference(['MESH_ID', 'DISEASE'])
    df[numeric_cols] = (df[numeric_cols].apply(pd.to_numeric, errors='coerce').round(3))

    df = df[df['cmpds'] > 4]
    df = df[df['BANDOCK-AF3_Diff'].abs() >= ia]
    # remove columns without word "Diff"
    df = df[[c for c in df.columns if 'Diff' in c or c in base]]
    df["DISEASE"] = df["DISEASE"].replace(disease_dict)
    print(f"{df_name} - {metric} threshold {ia}: {df.shape}")
    df.to_csv(f'{output_dir}/{metric}_{df_name}_comparison.tsv', sep='\t', index=False)
    return df

aia_ia = 41
nAIA_ia = 30
nNDCG_ia = 0.189
aiNDCG_ia = 0.103

df_AIA_current = process_df(df_AIA, df_name='AIA', ia=aia_ia, metric='current')
df_nAIA_current = process_df(df_nAIA, df_name='nAIA', ia=nAIA_ia, metric='current')
df_NDCG_current = process_df(df_NDCG, df_name='NDCG', ia=nNDCG_ia, metric='current')
df_AINDCG_current = process_df(df_AINDCG, df_name='AI-NDCG', ia=aiNDCG_ia, metric='current')

dfs = [df_AIA_current, df_nAIA_current, df_NDCG_current, df_AINDCG_current]
for i, df in enumerate(dfs):
    df["source"] = i

combined = pd.concat(dfs, ignore_index=True)
combined = combined.drop_duplicates(subset=["MESH_ID", "source"])

result = (combined.groupby(["MESH_ID", "DISEASE"])
                  .size()
                  .reset_index(name="Count")
                  .sort_values("Count", ascending=False))
result.to_csv(f'{output_dir}/counts.csv', index=False)
