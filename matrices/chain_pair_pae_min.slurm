#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48000
#SBATCH --time=23:00:00
#SBATCH --job-name=chain_pair_pae_min
#SBATCH --output=chain_pair_pae_min.out

start=$(date +%s)

srun --cpu-bind=cores ./chain_pair_pae_min.py

end=$(date +%s)
echo
echo "Total Slurm time: $((end - start)) seconds"