1. `scripts/1_prepare_smiles.py`: merge compound identifiers and SMILES data.
2. `scripts/2_prepare_input_jsons.py`: generate protein–ligand JSON inputs and reference A3M paths.
3. `scripts/3_generate_slurms.py`: make one SLURM script per interaction.
4. `scripts/4_submit_slurms_{cb,ea,gc}.py`: submit cluster-specific batches.

Support utilities and cluster-specific templates are retained in `scripts/`.

For archival reproducibility, use the same Python version, AF3 image, AF3 code revision, model parameters, database versions, JAX/CUDA/GPU platform, and seeds. Do not assume AF3 scores are identical between versions or accelerator systems.
