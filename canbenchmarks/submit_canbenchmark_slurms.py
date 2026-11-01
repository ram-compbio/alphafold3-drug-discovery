#!/usr/bin/env python3
import glob
import os
import subprocess

canbenchmarks = "af3/interactions/canbenchmarks"


for benchmark in os.listdir(f"{canbenchmarks}/new"):
    benchmark_dir = f"{canbenchmarks}/new/{benchmark}"
    aingcd_path = f"{benchmark_dir}/{benchmark}_aindcg.tsv"
    ania_path = f"{benchmark_dir}/{benchmark}_naia_nndcg.tsv"
    if os.path.exists(aingcd_path) or os.path.exists(ania_path):
        continue
    scripts_dir = f"{canbenchmarks}/new/{benchmark}/scripts"
    for script in glob.glob(f"{scripts_dir}/*.slurm"):
        print(f"Submitting {script} in {scripts_dir}")
        subprocess.run(["sbatch", os.path.basename(script)], cwd=scripts_dir,check=True)


for benchmark in os.listdir(f"{canbenchmarks}/old"):
    benchmark_dir = f"{canbenchmarks}/old/{benchmark}"
    aia_path = f"{benchmark_dir}/{benchmark}_aia.tsv"
    if os.path.exists(aia_path):
        continue
    scripts_dir = f"{canbenchmarks}/old/{benchmark}/scripts"
    for script in glob.glob(f"{scripts_dir}/*.slurm"):
        print(f"Submitting {script} in {scripts_dir}")
        subprocess.run(["sbatch", os.path.basename(script)], cwd=scripts_dir,check=True)