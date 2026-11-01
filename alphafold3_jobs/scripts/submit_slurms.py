#!/usr/bin/env python3
import os
import sys
import subprocess
from time import sleep
from datetime import datetime

def job_count(sbatch_args: str) -> int:
    sbatch_args = sbatch_args.split('-C')[0].strip()
    return int(subprocess.check_output(f"squeue {sbatch_args} -u $USER -h | wc -l", shell=True, stderr=subprocess.STDOUT).strip())

def has_output(slurm: str) -> bool:
    base = slurm.split('~')[0]
    stem = slurm.split('.')[0]
    ranking_scores = os.path.abspath(os.path.join(f"../../output/{base}", f"{stem}/{stem}_ranking_scores.csv"))
    return os.path.exists(ranking_scores)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sbatch_args = " ".join(sys.argv[1:])
slurm_files = [s for s in os.listdir(os.curdir) if s.endswith('.slurm')]

for slurm in slurm_files:
    if has_output(slurm):
        continue

    while True:
        current_jobs = job_count(sbatch_args)
        if current_jobs < 4:
            subprocess.run(f"sbatch {sbatch_args} {slurm} > /dev/null", check=True, shell=True)
            print(f"INFO[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Submitting {slurm}")
            break
        else:
            sleep(20) # Queue full. Waiting 20s

dir_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
file_name = os.path.basename(__file__)
print(f"INFO[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {dir_name}/{file_name}: all done!")