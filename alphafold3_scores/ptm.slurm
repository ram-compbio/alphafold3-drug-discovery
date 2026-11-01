#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48000
#SBATCH --time=23:00:00
#SBATCH --partition=compbio
#SBATCH --qos=compbio
#SBATCH --account=rams
#SBATCH --clusters=faculty
#SBATCH --job-name=ptm
#SBATCH --output=ptm.out

start=$(date +%s)

srun --cpu-bind=cores ./ptm.py

end=$(date +%s)
echo
echo "Total Slurm time: $((end - start)) seconds"