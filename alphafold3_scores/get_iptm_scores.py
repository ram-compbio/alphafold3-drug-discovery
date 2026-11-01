#!/usr/bin/env python3
import os
import json
import time
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

OUTPUT = "af3/interactions/output"
CCR_EAI = "af3/interactions/_scripts/lists/ccr_eai.txt"
MATRIX_DIR = "af3/interactions/canbenchmarks/matrices"

def process_pdb(pdb, metric):
    """
    Process one complete protein directory in a single worker.

    Returns:
        pdb ID and a dictionary of {cando_id: metric}.
    """
    output_dir = os.path.join(OUTPUT, pdb)
    scores = {}

    try:
        entries = os.scandir(output_dir)
    except OSError as exc:
        print(f"WARNING: Cannot read {output_dir}: {exc}", flush=True)
        return pdb, scores

    with entries:
        for entry in entries:
            if not entry.is_dir(follow_symlinks=False):
                continue

            pdb_cmpd = entry.name
            pdb_id, cando_id = pdb_cmpd.rsplit("~", 1)
            cando_id = int(cando_id)
            summary_json_path = os.path.join(entry.path, f"{pdb_cmpd}_summary_confidences.json")

            with open(summary_json_path, "r") as handle:
                scores[cando_id] = json.load(handle).get(metric)

    return pdb, scores


def main():
    metric = os.path.basename(__file__).replace(".py", "")
    start = time.perf_counter()

    # A set makes membership testing essentially instantaneous.
    completed = set(pd.read_csv(CCR_EAI, header=None, dtype=str).iloc[:, 0].dropna())

    # Only submit existing completed protein directories.
    pdbs = [entry.name for entry in os.scandir(OUTPUT) if entry.is_dir(follow_symlinks=False) and entry.name in completed]
    pdbs.sort()

    discovery_end = time.perf_counter()
    print(f"Protein directories: {len(pdbs)}", flush=True)
    print(f"Directory discovery: {discovery_end - start:.1f} seconds", flush=True)

    workers = int(os.environ.get("SLURM_CPUS_PER_TASK", "24"))
    rows = {}

    # Only one multiprocessing task per protein, rather than one per JSON file.
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for pdb, scores in executor.map(process_pdb, pdbs, [metric] * len(pdbs), chunksize=1):
            rows[pdb] = scores

    parsing_end = time.perf_counter()
    print(f"JSON processing: {(parsing_end - discovery_end) / 60:.2f} minutes", flush=True)

    # Dictionary keys become numeric CANDO columns.
    df = pd.DataFrame.from_dict(rows, orient="index")
    df.index.name = "pdb_id"

    # Match the previous pivot output ordering.
    df.sort_index(inplace=True)
    df = df.reindex(sorted(df.columns), axis=1)
    df.reset_index(inplace=True)

    rows, cols = df.shape[0], df.shape[1] - 1
    print(f"Output dimensions: {rows} x {cols}", flush=True)
    df.to_csv(os.path.join(MATRIX_DIR, f"{metric}_{rows}_{cols}.tsv"), sep="\t", index=False, header=False)

    end = time.perf_counter()
    print(f"Total time: {(end - start) / 60:.2f} minutes", flush=True)


if __name__ == "__main__":
    main()
