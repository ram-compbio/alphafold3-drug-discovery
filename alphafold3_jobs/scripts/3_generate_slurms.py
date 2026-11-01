#!/usr/bin/env python3
import os
import shutil
from concurrent.futures import ThreadPoolExecutor

basedir = '..'
input_jsons = f'{basedir}/input_jsons'
slurms_dir = f'{basedir}/slurms'

def slurm_template():
    with open('interaction_template.slurm', 'r') as obj:
        return obj.read()

TEMPLATE = slurm_template()  # read once

def process_file(file):
    protein_durg_id = file.split('.')[0]
    protein = protein_durg_id.split('~')[0]

    slurm_dir_protein = f'{slurms_dir}/{protein}'
    os.makedirs(slurm_dir_protein, exist_ok=True)
    os.makedirs(f'{slurm_dir_protein}/logs', exist_ok=True)

    shutil.copy('submit_slurms.py', f'{slurm_dir_protein}/')
    slurm_path = os.path.join(slurm_dir_protein, f'{protein_durg_id}.slurm')
    s_content = TEMPLATE.replace('xxxxx', protein_durg_id).replace('yyyyy', protein)

    with open(slurm_path, 'w') as slurm_obj:
        slurm_obj.write(s_content)

files = [f for f in os.listdir(input_jsons) if f.endswith('.json')]

with ThreadPoolExecutor(max_workers=len(os.sched_getaffinity(0))) as ex:
    list(ex.map(process_file, files))

