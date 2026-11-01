#!/projects/academic/rams/ratilala/venvs/af/bin/python3.10
import pandas as pd

df_ids = pd.read_csv("MESH_IDs.tsv", sep="\t")
df_tree = pd.read_csv("MESH_tree.tsv", sep="\t")
df_groups = pd.read_csv("MESH_groups.tsv", sep="\t")
df_manual = pd.read_csv("MESH_manual.tsv", sep="\t")

df_tree = df_tree.merge(df_groups, on="CATEGORY", how="left")
df_final = df_ids.merge(df_tree, on="MESH_ID", how="left")
df_concat = pd.concat([df_final, df_manual], axis=0, ignore_index=True)
df_final = (df_concat[["MESH_ID", "Disease", "GROUP",  "CATEGORY"]]
                  .dropna(subset=["GROUP"])
                  .drop_duplicates()
                  .sort_values(["CATEGORY", "GROUP"]))
df_final["MESH_ID"] = "MESH:" + df_final["MESH_ID"]
df_final.to_csv("MESH_IDs_grouped.tsv", sep="\t", index=False)

print(f"Unique indications        : {df_final['MESH_ID'].nunique()}")
print(f"Total rows (many-to-many) : {len(df_final)}")
