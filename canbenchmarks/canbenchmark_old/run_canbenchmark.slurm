#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --job-name=run_canbenchmark
#SBATCH --output=run_canbenchmark.out

start=`date +%s.%N`

./run_canbenchmark.py

end=`date +%s.%N`
echo -e "\nTotal Time: $(echo "($end - $start)/60" | bc) minutes"