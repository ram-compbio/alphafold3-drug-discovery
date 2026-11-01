### How AlphaFold 3 helps with multiscale drug discovery

This repository contains the computational workflows and analysis scripts used to evaluate AlphaFold 3 (AF3) interaction confidence scores for large scale drug repurposing using the Computational Analysis of Novel Drug Opportunities (CANDO) platform.

The study compares AF3 confidence scores with BANDOCK+ interaction scores and evaluates their performance using CANDO benchmarking metrics, including normalized average indication accuracy (nAIA) and normalized discounted cumulative gain (NDCG).

## Study overview

The analysis includes:

- 1,103 proteins modeled using AlphaFold 3.
- 2,449 approved compounds from the CANDO compound library.
- AF3 protein ligand interaction confidence scores, including ipTM.
- BANDOCK+ interaction matrices for comparison.
- Protein sublibraries selected by experimental PDB resolution and model pLDDT confidence.
- Random protein and interaction matrix controls.
- CANDO benchmarking using nAIA and NDCG.
- Comparative analysis of AF3 and BANDOCK+ performance.

## Repository structure

```text
AF3-CANDO/
├── alphafold3_jobs/
├── alphafold3_scores/
├── analysis_and_plots/
├── canbenchmarks/
├── canpredicts/
├── manifests/
├── matrices/
├── requirements.txt
└── README.md
```

| Directory | Description |
|---|---|
| `alphafold3_jobs/` | Scripts for AF3 input preparation, job submission, and output management |
| `alphafold3_scores/` | Scripts for extracting AF3 interaction confidence scores |
| `matrices/` | Scripts for generating and processing compound protein interaction matrices |
| `canbenchmarks/` | CANDO benchmarking scripts for nAIA and NDCG |
| `canpredicts/` | Compound prediction workflows |
| `analysis_and_plots/` | Scripts for statistical analysis and manuscript figures |
| `manifests/` | Dataset file inventories and reproducibility records |

## Data availability

The compound protein interaction matrices, benchmarking results, protein sublibraries, and associated analysis data are deposited separately in Dryad.

**Dryad dataset:** https://doi.org/10.5061/dryad.xsj3tx9z4

The dataset contains five directories:

- `analysis/`
- `canbenchmarks/`
- `cando_libraries/`
- `canpredicts/`
- `matrices/`

All interaction matrices and numerical benchmarking results are stored on Dryad rather than GitHub.

## Reproducibility

### 1. Clone the repository

```bash
git clone https://github.com/ram-compbio/alphafold3-drug-discovery.git
cd alphafold3-drug-discovery
```

Additional dependencies, including AlphaFold 3 and CANDO, must be installed separately according to the requirements of the relevant workflow.

### 2. Download the data

Download the dataset from Dryad and extract the archives into a local `data/` directory. Preserve the original directory structure.

```text
data/
├── analysis/
├── canbenchmarks/
├── cando_libraries/
├── canpredicts/
└── matrices/
```

### 3. Run the workflows

The repository provides scripts for the following stages:

1. AF3 input preparation and protein ligand complex prediction.
2. Extraction of AF3 interaction confidence scores.
3. Construction of compound protein interaction matrices.
4. CANDO benchmarking using nAIA and NDCG.
5. Downstream analysis and figure generation.

Individual scripts and SLURM job files document the relevant workflow operations. Execution paths and environment requirements should be configured for the target computing system.

## 4. Software and computational environment

AF3 predictions require a compatible AlphaFold 3 installation, model parameters, reference databases, and GPU computing resources.

The CANDO benchmarking workflows require the corresponding CANDO software and compound and indication libraries.

For strict reproduction, use the software versions, model configurations, and execution settings reported in the manuscript and associated computational environment records.

## Citation

If you use this repository or the associated dataset, please cite the corresponding manuscript:

How AlphaFold 3 helps with multiscale drug discovery
Ratilal Akabari, William Mangione, Zackary Falls, Ram Samudrala
2026.10.19.757941; doi: https://doi.org/10.64898/2026.10.19.757941 

## Contact

For questions regarding the computational workflows or associated datasets, please open a GitHub issue.