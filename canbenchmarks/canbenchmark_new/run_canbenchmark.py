#!/usr/bin/env python3
import sys
import os
sys.path.append('venvs/cando_latest')
import cando as cnd

inds_map = 'cmpds_inds/cmpds2inds-v2.2.tsv'
cmpd_map = 'cmpds_inds/drugbank-v2.8-approved.tsv'
matrix_file = 'matrix_path.tsv'
file_name = matrix_file.split('/')[-1].replace('.tsv', '')

cando = cnd.CANDO(cmpd_map,
                  inds_map,
                  matrix=matrix_file,
                  compute_distance=True,
                  dist_metric='cosine',
                  ncpus=12)

cando.canbenchmark_new(file_name, n=10, associated=True)
cando.canbenchmark_ndcg(file_name)

os.system('rm -rf canbenchmark* *.db time*')
os.system(f'mv summary*associated* ../{file_name}_naia_nndcg.tsv')
os.system(f'mv summary*ndcg* ../{file_name}_aindcg.tsv')