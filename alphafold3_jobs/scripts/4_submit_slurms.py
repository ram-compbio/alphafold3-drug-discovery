#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime
from _common import *

basedir = '..'
slurms_dir = f'{basedir}/slurms'
input_jsons = f'{basedir}/input_jsons'
output = f'{basedir}/output'

def find_completed(output):
    with open('completed.tsv') as f: pre_completed = [l.strip() for l in f if l.strip()]
    to_be_checked = list(set(os.listdir(output)) - set(pre_completed))
    completed = []
    for pdb in to_be_checked:
        prot = os.path.join(output, pdb)
        inter = os.listdir(prot)
        if len(inter) == 2449 and all(os.path.exists(os.path.join(prot, d, f"{d}_ranking_scores.csv")) for d in inter):
            completed.append(pdb)
    return completed

slurm_list = ['1d4uA', '1dgnA', '1e9tA', '1eigA', '1eotA', '1g2sA', '1haqA', '1hi7A']

completed = find_completed(output)
to_be_submitted = list(set(slurm_list) - set(completed))

for slurm_d in to_be_submitted:   
    submit_slurms_py = os.path.abspath(os.path.join(slurms_dir, slurm_d, 'submit_slurms.py'))
    subprocess.run(f'cp templates/submit_slurms_ea.py {submit_slurms_py}', check=True, shell=True)
    cmd = f'{python_interpreter} {submit_slurms_py} {sbatch_args}'
    subprocess.run(cmd, check=True, shell=True)

print(f"INFO[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {os.path.basename(__file__)}: all done!")