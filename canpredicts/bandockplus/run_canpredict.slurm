#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --job-name=run_canpredict
#SBATCH --output=run_canpredict.out

start=`date +%s.%N`

./run_canpredict.py

end=`date +%s.%N`
echo -e "\nTotal Time: $(echo "($end - $start)/60" | bc) minutes"