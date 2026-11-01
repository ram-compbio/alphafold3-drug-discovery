#!/usr/bin/env python3
import os
import pandas as pd
import shutil
import json
import copy

basedir = '..'
input_jsons_no_interactions = f'{basedir}/input_jsons_no_interactions'
input_jsons_interactions = f'{basedir}/input_jsons'
tsv_file = 'drugbank-v2.8-approved_smile.tsv'
ligand_df = pd.read_csv(tsv_file, sep='\t')

def add_3m_and_ligand(input_json_path, output_dir, ligand_details_df):
    """
    Reads the protein JSON from input_json_path
    creates a new JSON file that includes:
      - The protein details with updated MSA paths.
      - An updated "name" field that is: original_name~CANDO_ID.
      - A new "ligand" entry appended to "sequences".
    """
    with open(input_json_path, 'r') as infile:
        original_data = json.load(infile)
    
    original_name = original_data.get("name", "")
    msa_path = f"./a3m/{original_name}.a3m"
    
    for idx, row in ligand_details_df.iterrows():
        CANDO_ID = row['CANDO_ID']
        smile = row['SMILE']
        modified_data = copy.deepcopy(original_data)
        for seq in modified_data.get("sequences", []):
            if "protein" in seq:
                protein = seq["protein"]
                protein["unpairedMsaPath"] = msa_path
                protein["pairedMsaPath"] = msa_path
                seq["protein"] = protein

        modified_data["name"] = f"{original_name}~{CANDO_ID}"
        ligand_entry = {"ligand": {"id": "XYZ",
                        "smiles": smile}}
        modified_data.get("sequences", []).append(ligand_entry)
        output_json_filename = modified_data["name"] + ".json"
        output_json_path = os.path.join(output_dir, output_json_filename)

        with open(output_json_path, 'w') as outfile:
            json.dump(modified_data, outfile, indent=2)
        
        print(f"Created {output_json_path}")

for input_json_plain in os.listdir(input_jsons_no_interactions):
    input_json_plain_name = input_json_plain.split('.')[0]
    input_json_plain_path = os.path.join(input_jsons_no_interactions, input_json_plain)
    add_3m_and_ligand(input_json_plain_path, input_jsons_interactions, ligand_df)

count = len(os.listdir(input_jsons_interactions))
print(f'Total JSON files with interactions created: {count}')
