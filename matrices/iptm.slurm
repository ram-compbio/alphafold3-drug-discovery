#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48000
#SBATCH --time=23:00:00
#SBATCH --job-name=iptm
#SBATCH --output=iptm.out

start=$(date +%s)

srun --cpu-bind=cores ./iptm.py

end=$(date +%s)
echo
echo "Total Slurm time: $((end - start)) seconds"