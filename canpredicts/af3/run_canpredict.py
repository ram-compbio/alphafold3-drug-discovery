#!/usr/bin/env python3
import sys
import os
import pandas as pd
import subprocess
sys.path.append('venvs/cando_latest')
import cando as cnd

inds_map = 'cmpds_inds/cmpds2inds-v2.2.tsv'
cmpd_map = 'cmpds_inds/drugbank-v2.8-approved.tsv'
matrix_file = 'af3/interactions/canbenchmarks/matrices/iptm_1103_2449.tsv'

cando = cnd.CANDO(cmpd_map,
                  inds_map,
                  matrix=matrix_file,
                  compute_distance=True,
                  dist_metric='cosine',
                  ncpus=48)

mesh_ids = pd.read_csv(inds_map, sep='\t', dtype=str)['MESH_ID'].unique().tolist()

for mesh_id in mesh_ids:
    try:
        indication = cando.get_indication(mesh_id)
        canpredict_compounds_dir = 'canpredict_compounds_n_10'
        os.makedirs(canpredict_compounds_dir, exist_ok=True)
        predicted_compounds_file = f'{canpredict_compounds_dir}/{indication.name}~{mesh_id}.tsv'
        
        print(f'Running canpredict_compounds for: {mesh_id}')
        cando.canpredict_compounds(mesh_id, n=10, topX=10, save=predicted_compounds_file)

        with open(predicted_compounds_file, 'r') as f:
            if len(f.readlines()) <= 1:
                os.remove(predicted_compounds_file) 
                
    except Exception:
        pass
