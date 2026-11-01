#!/usr/bin/env python3
import pandas as pd
import os
import shutil

input_dir = "outputs/6_compare_individual_accuracies_current"
base_name = os.path.splitext(os.path.basename(__file__))[0]
output_dir = f'../outputs/{base_name}'
os.system(f"rm -rf {output_dir}")
os.makedirs(output_dir, exist_ok=True)
af3_canpredicts_dir = "af3/canpredicts/af3_current/canpredict_compounds_n_10"
bandockplus_canpredicts_dir = "af3/canpredicts/bandockplus_current/canpredict_compounds_n_10"


naia = pd.read_csv(f'{input_dir}/current_nAIA_comparison.tsv', sep="\t")[['MESH_ID', 'DISEASE', 'cmpds']]
ndcg = pd.read_csv(f'{input_dir}/current_NDCG_comparison.tsv', sep="\t")[['MESH_ID', 'DISEASE', 'cmpds']]
common = naia.merge(ndcg, on=['MESH_ID', 'DISEASE', 'cmpds'])
common.to_csv(f"{output_dir}/common_indications.tsv", sep="\t", index=False)
mesh_ids = common['MESH_ID'].tolist()


for prediction in os.listdir(af3_canpredicts_dir):
    mesh_id = prediction.split("~")[1].split(".")[0]
    if mesh_id in mesh_ids:
        prediction_path = f"{af3_canpredicts_dir}/{prediction}"
        new_prediction_name = f"BANDOCKPLUS_{prediction.replace(' ', '_').replace(':', '_')}"
        shutil.copy(f"{af3_canpredicts_dir}/{prediction}", f"{output_dir}/AF3_{new_prediction_name}")

for prediction in os.listdir(bandockplus_canpredicts_dir):
    mesh_id = prediction.split("~")[1].split(".")[0]
    if mesh_id in mesh_ids:
        prediction_path = f"{bandockplus_canpredicts_dir}/{prediction}"
        new_prediction_name = f"BANDOCKPLUS_{prediction.replace(' ', '_').replace(':', '_')}"
        shutil.copy(f"{bandockplus_canpredicts_dir}/{prediction}", f"{output_dir}/{new_prediction_name}")

bandockplus_matrix_file = 'af3/interactions/canbenchmarks/matrices/bandockplus_1103_2449.tsv'
af3_matrix_file = 'af3/interactions/canbenchmarks/matrices/iptm_1103_2449.tsv'
approved = 'drugbank-v2.8-approved.tsv'
metadata_file = 'homo_sapien-metadata.tsv'

outputs = {
    "7948_bandockplus": f'{output_dir}/ribociclib_7948_bandockplus.tsv',
    "454_bandockplus": f'{output_dir}/vinblastine_454_bandockplus.tsv',
    "7948_af3": f'{output_dir}/ribociclib_7948_af3.tsv',
    "454_af3": f'{output_dir}/vinblastine_454_af3.tsv'
}

bandockplus_matrix = pd.read_csv(bandockplus_matrix_file, sep="\t", header=None)
af3_matrix = pd.read_csv(af3_matrix_file, sep="\t", header=None)
drugbank = pd.read_csv(approved, sep="\t")
metadata = pd.read_csv(metadata_file, sep="\t")

cando_ids = drugbank["CANDO_ID"].astype(str).tolist()
header = [""] + cando_ids
cando_to_col = {int(cid): i + 1 for i, cid in enumerate(cando_ids)}
drug_names = drugbank.set_index("CANDO_ID")["GENERIC_NAME"].to_dict()

def process_signature(df, cando_id, output):
    out = pd.concat([pd.DataFrame([header]), df], ignore_index=True)
    out = out.iloc[:, [0, cando_to_col[cando_id]]]
    out.iloc[0] = ["PDB_ID", f"{cando_id}({drug_names[cando_id]})"]
    out = pd.concat([out.iloc[[0]], out.iloc[1:].sort_values(by=out.columns[1], ascending=False)], ignore_index=True)
    out = pd.concat([out.iloc[[0]], out.iloc[1:].merge(metadata[["PDB_ID", "GENE_NAME", "PROT_NAME"]], left_on=0, right_on="PDB_ID", how="left").drop(columns=["PDB_ID"])], ignore_index=True)
    out.iloc[0] = ["PDB_ID", f"{cando_id}({drug_names[cando_id]})", "GENE_NAME", "PROT_NAME"]
    out.to_csv(output, sep="\t", index=False, header=False)

for df, prefix in [(bandockplus_matrix, "bandockplus"), (af3_matrix, "af3")]:
    for cando_id in [7948, 454]:
        process_signature(df, cando_id, outputs[f"{cando_id}_{prefix}"])