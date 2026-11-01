#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=24000
#SBATCH --gres=gpu:1
#SBATCH --time=00:50:00
#SBATCH --job-name=xxxxx
#SBATCH --output=logs/xxxxx.out

start=$(date +%s)

nvidia-smi -L

base_path="../.."
af3_bin="$base_path/run_alphafold3"
input_json="$base_path/input_jsons/xxxxx.json"
output_dir="$base_path/output/yyyyy/xxxxx"

job_name=$(jq -r '.name' "$input_json")
sanitised_name=$(echo "$job_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd 'a-z0-9_.-')
output_dir_sub="${output_dir}/${sanitised_name}"

mkdir -p "$output_dir"
find "$output_dir" -mindepth 1 -exec rm -rf {} + # rm any previous incomplete runs
"$af3_bin" "$input_json" "$output_dir"

# Perform cleanup & Renaming
cd "$output_dir_sub"
rm -r seed-* TERMS_OF_USE.md *_data.json "${sanitised_name}_confidences.json"
mv "${sanitised_name}_summary_confidences.json" "${job_name}_summary_confidences.json"
mv "${sanitised_name}_model.cif" "${job_name}_model.cif"
mv ranking_scores.csv "${job_name}_ranking_scores.csv"
sed -i "s/${sanitised_name}/${job_name}/g" "${job_name}_model.cif"
cd .. && mv ${sanitised_name}/* . && rm -r ${sanitised_name}

end=$(date +%s)
echo -e "\nTotal Time: $(( (end - start)/60 )) minute(s) $(( (end - start)%60 )) second(s)"