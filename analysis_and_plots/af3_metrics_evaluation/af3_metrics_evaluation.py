#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd


def flatten_tsv(input_file):
    df = pd.read_csv(input_file, sep='\t').iloc[:, :5]
    flattened_data = {}
    for row in df.itertuples(index=False):
        for col_name, value in zip(df.columns, row):
            if any(x in col_name for x in ['top25', 'top50', 'top100', 'Unnamed', 'control']):
                continue
            flattened_data[f"{row[0]}"] = value

    flattened_df = pd.DataFrame(flattened_data, index=[0])
    matrix = os.path.basename(os.path.dirname(input_file))
    flattened_df.insert(0, 'Matrix', matrix)

    return flattened_df


def bulk_flatten(canbenchmarks_dir, include_ndcg):
    aia_dfs = []
    ndcg_dfs = []

    for matrix in os.listdir(canbenchmarks_dir):
        matrix_path = os.path.join(canbenchmarks_dir, matrix)
        if not os.path.isdir(matrix_path):
            continue
        for summary_file in os.listdir(matrix_path):
            summary_file_path = os.path.join(matrix_path, summary_file)
            if not os.path.isfile(summary_file_path):
                continue
            if summary_file.endswith('_naia_nndcg.tsv') or summary_file.endswith('_aia.tsv'):
                # print(f"Flattening {summary_file_path}")
                aia_dfs.append(flatten_tsv(summary_file_path))
            elif include_ndcg and summary_file.endswith('_aindcg.tsv'):
                # print(f"Flattening {summary_file_path}")
                ndcg_dfs.append(flatten_tsv(summary_file_path))

    if not aia_dfs:
        raise ValueError(f"No AIA summary files found in {canbenchmarks_dir}")

    aia_combined_df = pd.concat(aia_dfs, ignore_index=True)
    if include_ndcg:
        if not ndcg_dfs:
            raise ValueError(f"No ai-NDCG summary files found in {canbenchmarks_dir}")
        ndcg_combined_df = pd.concat(ndcg_dfs, ignore_index=True)
        combined_df = pd.merge(aia_combined_df, ndcg_combined_df, on='Matrix', how='left')
    else:
        combined_df = aia_combined_df
    combined_df = combined_df.loc[:, ~combined_df.columns.str.contains('control|Control', regex=True)]

    return combined_df


def calculate_sem(input_file):
    """Calculate SEM from the top10 column."""
    df = pd.read_csv(input_file, sep='\t')
    values = pd.to_numeric(df['top10'], errors='coerce').dropna()
    if len(values) < 2:
        return np.nan
    return round(values.std(ddof=1) / np.sqrt(len(values)), 5)


def collect_sem(canbenchmarks_dir, include_ndcg):
    """Collect SEM values for every matrix."""
    rows = []

    for matrix in os.listdir(canbenchmarks_dir):
        matrix_path = os.path.join(canbenchmarks_dir, matrix)

        if not os.path.isdir(matrix_path) or '_purge' in matrix:
            continue

        results_dir = os.path.join(matrix_path, 'scripts', 'results_analysed_named')

        if not os.path.isdir(results_dir):
            continue

        row = {'Matrix': matrix}

        if include_ndcg:
            row.update({'nAIA_SEM': np.nan, 'nNDCG_SEM': np.nan, 'ai-ndcg_SEM': np.nan})
        else:
            row['aia_SEM'] = np.nan

        for filename in os.listdir(results_dir):
            input_file = os.path.join(results_dir, filename)

            if not os.path.isfile(input_file) or not filename.endswith('.tsv'):
                continue

            # New nAIA or old AIA results
            if 'ndcg' not in filename:
                if include_ndcg:
                    row['nAIA_SEM'] = calculate_sem(input_file)
                else:
                    row['aia_SEM'] = calculate_sem(input_file)

            # New nNDCG results
            elif 'ndcg' in filename and 'associated' in filename and include_ndcg:
                row['nNDCG_SEM'] = calculate_sem(input_file)

            # New ai-NDCG results
            elif 'ndcg' in filename and 'associated' not in filename and include_ndcg:
                row['ai-ndcg_SEM'] = calculate_sem(input_file)

        rows.append(row)

    return pd.DataFrame(rows)


af3_new = 'canbenchmarks/new'
af3_old = 'canbenchmarks/old'

# Read summary values.
af3_new_df = bulk_flatten(af3_new, include_ndcg=True)
af3_old_df = bulk_flatten(af3_old, include_ndcg=False)
af3 = pd.merge(af3_new_df, af3_old_df, on='Matrix', how='left')

# Calculate SEM from the underlying result files.
new_sem_df = collect_sem(af3_new, include_ndcg=True)
old_sem_df = collect_sem(af3_old, include_ndcg=False)
sem_df = pd.merge(new_sem_df, old_sem_df, on='Matrix', how='left')

# Add SEM columns to the summary results.
af3 = pd.merge(af3, sem_df, on='Matrix', how='left')

# Keep and arrange only the requested values and their SEM.
af3 = af3[['Matrix', 'nAIA', 'nAIA_SEM', 'nNDCG', 'nNDCG_SEM', 'ai-ndcg', 'ai-ndcg_SEM', 'aia', 'aia_SEM']]

# Replace random-n etc. with one mean row.
control_mask = af3['Matrix'].str.match(r'^random-\d+$', na=False)

if control_mask.any():
    numeric_columns = ['nAIA', 'nAIA_SEM', 'nNDCG', 'nNDCG_SEM', 'ai-ndcg', 'ai-ndcg_SEM', 'aia', 'aia_SEM']
    control_average = af3.loc[control_mask, numeric_columns].apply(pd.to_numeric, errors='coerce').mean().round(5)
    control_row = control_average.to_frame().T
    control_row.insert(0, 'Matrix', 'control')
    af3 = pd.concat([af3.loc[~control_mask], control_row], ignore_index=True)

af3[numeric_columns] = af3[numeric_columns].round(3)
# Matric column values replace text with something else
af3['Matrix'] = af3['Matrix'].str.replace('control', 'Control')
af3['Matrix'] = af3['Matrix'].str.replace('_1141_2449', '')
af3['Matrix'] = af3['Matrix'].str.replace('_', ' ')
af3['Matrix'] = af3['Matrix'].str.replace('tm', 'TM')
af3['Matrix'] = af3['Matrix'].str.replace('chain pair', 'Chain-pair')
af3['Matrix'] = af3['Matrix'].str.replace('ranking score', 'Ranking Score')

# column rename
af3 = af3.rename(columns={'nNDCG': 'NDCG',
                          'nNDCG_SEM': 'NDCG_SEM',
                          'ai-ndcg': 'AI-NDCG',
                          'ai-ndcg_SEM': 'AI-NDCG_SEM',
                          'aia': 'AIA',
                          'aia_SEM': 'AIA_SEM'})

base_name = os.path.splitext(os.path.basename(__file__))[0]
csv_path = f'outputs/{base_name}.tsv'
af3.to_csv(csv_path, sep='\t', index=False)
print(f'Saved: {csv_path}')