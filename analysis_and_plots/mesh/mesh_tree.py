#!/projects/academic/rams/ratilala/venvs/af/bin/python3.10
import os
import xml.etree.ElementTree as ET
import pandas as pd

# wget https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc2025.gz
# gzip -dv desc2025.gz
# mv desc2025 desc2025.xml
xml_file = "desc2025.xml"

tree = ET.parse(xml_file)
root = tree.getroot()

rows = []

for record in root.findall(".//DescriptorRecord"):
    mesh_id = record.findtext("DescriptorUI")
    tree_list = record.find("TreeNumberList")
    descriptor_name = record.findtext("DescriptorName/String")

    if tree_list is not None:
        for tn in tree_list.findall("TreeNumber"):
            tn = tn.text
            if tn.startswith("C"):
                rows.append({"MESH_ID": mesh_id, "TREE_NUMBER": tn, "CATEGORY": tn.split('.')[0], "DISEASE": descriptor_name})

df_tree = pd.DataFrame(rows)
df_tree.to_csv("MESH_TREE.tsv", sep='\t', index=False)