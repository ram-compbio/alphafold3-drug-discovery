#!/usr/bin/env python3
import os
import shutil

canbenchmarks = "af3/interactions/canbenchmarks"
matrix_dir = f'{canbenchmarks}/matrices'
templates = {f"{canbenchmarks}/new": "canbenchmark_new", 
             f"{canbenchmarks}/old": "canbenchmark_old"}

def create_scripts(matrix_name, output_dir, template_dir):
    scripts_dir = f"{output_dir}/{matrix_name}/scripts"
    os.makedirs(scripts_dir, exist_ok=True)

    for filename in os.listdir(template_dir):
        src = f"{template_dir}/{filename}"
        dst = f"{scripts_dir}/{filename.replace('run_canbenchmark', matrix_name)}"

        shutil.copy(src, dst)

        with open(dst) as file:
            content = file.read()

        with open(dst, "w") as file:
            content = content.replace("matrix_path.tsv", f"{matrix_dir}/{matrix_name}.tsv")
            content = content.replace("run_canbenchmark", matrix_name)
            file.write(content)


for matrix in os.listdir(matrix_dir):
    if not matrix.endswith(".tsv"):
        continue
    if "af2" not in matrix:
        continue
    matrix_name = os.path.splitext(matrix)[0]
    print(f"Creating directory for: {matrix_name}")

    for output_dir, template_dir in templates.items():
        create_scripts(matrix_name, output_dir, template_dir)
