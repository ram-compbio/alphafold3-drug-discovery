#!/usr/bin/env python3
import os
import re
import glob
import pandas as pd


def filter_pdb_ids_by_tag(keyword):
    """Read PDB_ID and TAG, filter TAG by substring, and write PDB_IDs to TSV."""
    data = pd.read_excel("homo_sapien-metadata.xlsx", usecols=["PDB_ID", "TAG"])
    matches = data["TAG"].astype("string").str.contains(str(keyword), case=False, na=False, regex=False)
    result = data.loc[matches, ["PDB_ID"]].dropna()
    keyword = keyword.lower()
    output_file = f"{keyword}.csv" if any(tag in keyword for tag in ("top", "bottom", "random")) else f"all200_{keyword}.csv"
    result.to_csv(output_file, header=False, index=False)

    print("Matched rows:", len(result))
    print("Output file:", output_file)
    return output_file


def filter_current_matrix():
    '''Filter the current iptm matrix after iptm.py has run
    and write the PDB IDs to a CSV file, current_<number_of_rows>.csv.'''
    input_file = glob.glob("af3/interactions/canbenchmarks/matrices/iptm_*_2449.tsv")[0]
    with open(input_file, "r", encoding="utf-8") as fin:
        lines = fin.readlines()
    with open(f"current_{len(lines)}.csv", "w", encoding="utf-8") as fout:
        for line in lines:
            first_col = line.rstrip("\n").split("\t")[0]
            fout.write(first_col + "\n")

if __name__ == "__main__":
    filter_pdb_ids_by_tag(keyword="Random200")
    filter_pdb_ids_by_tag(keyword="Top100_RES")
    filter_pdb_ids_by_tag(keyword="Bottom100_RES")
    filter_pdb_ids_by_tag(keyword="Top100_pLDDT")
    filter_pdb_ids_by_tag(keyword="Bottom100_pLDDT")
    filter_pdb_ids_by_tag(keyword="RES")
    filter_pdb_ids_by_tag(keyword="pLDDT")

    filter_current_matrix()
