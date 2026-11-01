#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=48000
#SBATCH --time=23:00:00
#SBATCH --job-name=ranking_score
#SBATCH --output=ranking_score.out

start=$(date +%s)

srun --cpu-bind=cores ./ranking_score.py

end=$(date +%s)
echo
echo "Total Slurm time: $((end - start)) seconds"