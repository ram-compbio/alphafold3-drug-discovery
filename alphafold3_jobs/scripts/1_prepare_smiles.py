#!/usr/bin/env python3
import os
import pandas as pd

all_df = pd.read_csv('all_all.smi', sep='\t', header=None)
all_df = all_df[[1, 0]]
all_df.columns = ['GENERIC_NAME', 'SMILE']
all_df = all_df.drop_duplicates()

approved_df = pd.read_csv('drugbank-v2.8-approved.tsv', sep='\t')
approved_df = approved_df.drop(columns=['DRUGBANK_ID', 'DRUG_GROUPS'])
approved_df = approved_df.drop_duplicates()

merged_df = approved_df.merge(all_df)
merged_df = merged_df.drop_duplicates(subset=['GENERIC_NAME', 'SMILE'])
merged_df = merged_df.drop_duplicates(subset=['CANDO_ID'], keep='last')
merged_df = merged_df.drop(columns=['GENERIC_NAME'])
merged_df.to_csv('drugbank-v2.8-approved_smile2.tsv', sep='\t', index=False)