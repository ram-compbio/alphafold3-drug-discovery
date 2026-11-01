#!/usr/bin/env python3
import pandas as pd
import os
import re

new_bandock_plddt = 'af3/interactions/canbenchmarks/new/bandockplus_all200_plddt/scripts/results_analysed_named'
new_bandock_res = 'af3/interactions/canbenchmarks/new/bandockplus_all200_res/scripts/results_analysed_named'
new_bandock_random200 = 'af3/interactions/canbenchmarks/new/bandockplus_random200/scripts/results_analysed_named'
new_af3_plddt = 'af3/interactions/canbenchmarks/new/iptm_all200_plddt/scripts/results_analysed_named'
new_af3_res = 'af3/interactions/canbenchmarks/new/iptm_all200_res/scripts/results_analysed_named'
new_af3_random200 = 'af3/interactions/canbenchmarks/new/iptm_random200/scripts/results_analysed_named'

old_bandock_plddt = 'af3/interactions/canbenchmarks/old/bandockplus_all200_plddt/scripts/results_analysed_named'
old_bandock_res = 'af3/interactions/canbenchmarks/old/bandockplus_all200_res/scripts/results_analysed_named'
old_bandock_random200 = 'af3/interactions/canbenchmarks/old/bandockplus_random200/scripts/results_analysed_named'
old_af3_plddt = 'af3/interactions/canbenchmarks/old/iptm_all200_plddt/scripts/results_analysed_named'
old_af3_res = 'af3/interactions/canbenchmarks/old/iptm_all200_res/scripts/results_analysed_named'
old_af3_random200 = 'af3/interactions/canbenchmarks/old/iptm_random200/scripts/results_analysed_named'


nAIA_bandock_plddt = f'{new_bandock_plddt}/results_analysed_named-bandockplus_all200_plddt-10-associated.tsv'
nNDCG_bandock_plddt = f'{new_bandock_plddt}/results_analysed_named-ndcg-bandockplus_all200_plddt-10-associated.tsv'
aiNDCG_bandock_plddt = f'{new_bandock_plddt}/results_analysed_named_ndcg-bandockplus_all200_plddt.tsv'
nAIA_bandock_res = f'{new_bandock_res}/results_analysed_named-bandockplus_all200_res-10-associated.tsv'
nNDCG_bandock_res = f'{new_bandock_res}/results_analysed_named-ndcg-bandockplus_all200_res-10-associated.tsv'
aiNDCG_bandock_res = f'{new_bandock_res}/results_analysed_named_ndcg-bandockplus_all200_res.tsv'
nAIA_bandock_random200 = f'{new_bandock_random200}/results_analysed_named-bandockplus_random200-10-associated.tsv'
nNDCG_bandock_random200 = f'{new_bandock_random200}/results_analysed_named-ndcg-bandockplus_random200-10-associated.tsv'
aiNDCG_bandock_random200 = f'{new_bandock_random200}/results_analysed_named_ndcg-bandockplus_random200.tsv'
nAIA_af3_plddt = f'{new_af3_plddt}/results_analysed_named-iptm_all200_plddt-10-associated.tsv'
nNDCG_af3_plddt = f'{new_af3_plddt}/results_analysed_named-ndcg-iptm_all200_plddt-10-associated.tsv'
aiNDCG_af3_plddt = f'{new_af3_plddt}/results_analysed_named_ndcg-iptm_all200_plddt.tsv'
nAIA_af3_res = f'{new_af3_res}/results_analysed_named-iptm_all200_res-10-associated.tsv'
nNDCG_af3_res = f'{new_af3_res}/results_analysed_named-ndcg-iptm_all200_res-10-associated.tsv'
aiNDCG_af3_res = f'{new_af3_res}/results_analysed_named_ndcg-iptm_all200_res.tsv'
nAIA_af3_random200 = f'{new_af3_random200}/results_analysed_named-iptm_random200-10-associated.tsv'
nNDCG_af3_random200 = f'{new_af3_random200}/results_analysed_named-ndcg-iptm_random200-10-associated.tsv'
aiNDCG_af3_random200 = f'{new_af3_random200}/results_analysed_named_ndcg-iptm_random200.tsv'


oAIA_bandock_plddt = f'{old_bandock_plddt}/results_analysed_named-bandockplus_all200_plddt.tsv'
oAIA_bandock_res = f'{old_bandock_res}/results_analysed_named-bandockplus_all200_res.tsv'
oAIA_bandock_random200 = f'{old_bandock_random200}/results_analysed_named-bandockplus_random200.tsv'
oAIA_af3_plddt = f'{old_af3_plddt}/results_analysed_named-iptm_all200_plddt.tsv'
oAIA_af3_res = f'{old_af3_res}/results_analysed_named-iptm_all200_res.tsv'
oAIA_af3_random200 = f'{old_af3_random200}/results_analysed_named-iptm_random200.tsv'

results = { 'nAIA_BANDOCK_pLDDT': nAIA_bandock_plddt,
            'nNDCG_BANDOCK_pLDDT': nNDCG_bandock_plddt,
            'aiNDCG_BANDOCK_pLDDT': aiNDCG_bandock_plddt,
            'nAIA_BANDOCK_resolution': nAIA_bandock_res,
            'nNDCG_BANDOCK_resolution': nNDCG_bandock_res,
            'aiNDCG_BANDOCK_resolution': aiNDCG_bandock_res,
            'nAIA_BANDOCK_unbiased': nAIA_bandock_random200,
            'nNDCG_BANDOCK_unbiased': nNDCG_bandock_random200,
            'aiNDCG_BANDOCK_unbiased': aiNDCG_bandock_random200,
            'nAIA_AF3_pLDDT': nAIA_af3_plddt,
            'nNDCG_AF3_pLDDT': nNDCG_af3_plddt,
            'aiNDCG_AF3_pLDDT': aiNDCG_af3_plddt,
            'nAIA_AF3_resolution': nAIA_af3_res,
            'nNDCG_AF3_resolution': nNDCG_af3_res,
            'aiNDCG_AF3_resolution': aiNDCG_af3_res,
            'nAIA_AF3_unbiased': nAIA_af3_random200,
            'nNDCG_AF3_unbiased': nNDCG_af3_random200,
            'aiNDCG_AF3_unbiased': aiNDCG_af3_random200,
            'oAIA_BANDOCK_pLDDT': oAIA_bandock_plddt,
            'oAIA_BANDOCK_resolution': oAIA_bandock_res,
            'oAIA_BANDOCK_unbiased': oAIA_bandock_random200,
            'oAIA_AF3_pLDDT': oAIA_af3_plddt,
            'oAIA_AF3_resolution': oAIA_af3_res,
            'oAIA_AF3_unbiased': oAIA_af3_random200
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

    BANDOCK_pLDDT = [c for c in metrics if 'BANDOCK_pLDDT' in c][0]
    BANDOCK_resolution = [c for c in metrics if 'BANDOCK_resolution' in c][0]
    BANDOCK_unbiased = [c for c in metrics if 'BANDOCK_unbiased' in c][0]
    AF3_pLDDT = [c for c in metrics if 'AF3_pLDDT' in c][0]
    AF3_resolution = [c for c in metrics if 'AF3_resolution' in c][0]
    AF3_unbiased = [c for c in metrics if 'AF3_unbiased' in c][0]

    df['BANDOCK_pLDDT-AF3_pLDDT_Diff'] = (df[BANDOCK_pLDDT] - df[AF3_pLDDT])
    df['BANDOCK_resolution-AF3_resolution_Diff'] = (df[BANDOCK_resolution] - df[AF3_resolution])
    df['BANDOCK_unbiased-AF3_unbiased_Diff'] = (df[BANDOCK_unbiased] - df[AF3_unbiased])

    diff_cols = ['BANDOCK_pLDDT-AF3_pLDDT_Diff', 'BANDOCK_resolution-AF3_resolution_Diff', 'BANDOCK_unbiased-AF3_unbiased_Diff']
    df = df[base + metrics + diff_cols]

    numeric_cols = df.columns.difference(['MESH_ID', 'DISEASE'])
    df[numeric_cols] = (df[numeric_cols].apply(pd.to_numeric, errors='coerce').round(3))

    df = df[df['cmpds'] > 4]
    df = df[df[f'BANDOCK_{metric}-AF3_{metric}_Diff'].abs() >= ia]
    # remove columns without word "Diff"
    df = df[[c for c in df.columns if 'Diff' in c or c in base]]
    df = df[[c for c in df.columns if metric in c or c in base]]
    df["DISEASE"] = df["DISEASE"].replace(disease_dict)
    print(f"{df_name} - {metric} threshold {ia}: {df.shape}")
    df.to_csv(f'{output_dir}/{metric}_{df_name}_comparison.tsv', sep='\t', index=False)
    return df

aia_ia = 41
nAIA_ia = 30
nNDCG_ia = 0.189
aiNDCG_ia = 0.103

df_AIA_pLDDT = process_df(df_AIA, df_name='AIA', ia=aia_ia, metric='pLDDT')
df_nAIA_pLDDT = process_df(df_nAIA, df_name='nAIA', ia=nAIA_ia, metric='pLDDT')
df_NDCG_pLDDT = process_df(df_NDCG, df_name='NDCG', ia=nNDCG_ia, metric='pLDDT')
df_AINDCG_pLDDT = process_df(df_AINDCG, df_name='AI_NDCG', ia=aiNDCG_ia, metric='pLDDT')

df_AIA_resolution = process_df(df_AIA, df_name='AIA', ia=aia_ia, metric='resolution')
df_nAIA_resolution = process_df(df_nAIA, df_name='nAIA', ia=nAIA_ia, metric='resolution')
df_NDCG_resolution = process_df(df_NDCG, df_name='NDCG', ia=nNDCG_ia, metric='resolution')
df_AINDCG_resolution = process_df(df_AINDCG, df_name='AI_NDCG', ia=aiNDCG_ia, metric='resolution')

df_AIA_unbiased = process_df(df_AIA, df_name='AIA', ia=aia_ia, metric='unbiased')
df_nAIA_unbiased = process_df(df_nAIA, df_name='nAIA', ia=nAIA_ia, metric="unbiased")
df_NDCG_unbiased = process_df(df_NDCG,df_name="NDCG", ia=nNDCG_ia, metric="unbiased")
df_AINDCG_unbiased = process_df(df_AINDCG,df_name="AI_NDCG", ia=aiNDCG_ia, metric="unbiased")


dfs = [df_AIA_pLDDT, df_nAIA_pLDDT, df_NDCG_pLDDT, df_AINDCG_pLDDT, df_AIA_resolution, df_nAIA_resolution, df_NDCG_resolution, df_AINDCG_resolution, df_AIA_unbiased, df_nAIA_unbiased, df_NDCG_unbiased, df_AINDCG_unbiased]
for i, df in enumerate(dfs):
    df["source"] = i

combined = pd.concat(dfs, ignore_index=True)
combined = combined.drop_duplicates(subset=["MESH_ID", "source"])

result = (combined.groupby(["MESH_ID", "DISEASE"])
                  .size()
                  .reset_index(name="Count")
                  .sort_values("Count", ascending=False))
result.to_csv(f'{output_dir}/counts.csv', index=False)
