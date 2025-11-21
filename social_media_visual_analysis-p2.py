# -*- coding: utf-8 -*-
"""
Created on Wed Nov 05 20:00:00 2025

@author: Elvison

Script para selecionar e salvar imagens de amostra para cada cluster refinado.
"""
import os
import datetime
from clustering.change_images import copy_images_to_cluster_folders

superStartTime = datetime.datetime.now()
print("Comecou tudo em ", superStartTime)

# --- CONFIGURAÇÕES DO USUÁRIO ---
# 1. Defina o nome da coluna que contém seus clusters refinados.
cluster_column_name = "Clustering_refined"  # Exemplo: "Agrupamento Refinado 1"

# --- Caminhos (geralmente não precisam ser alterados) ---
path_refined_clustering = 'outputs/clustering/refined'
path_normalized_posts = 'outputs/normalize_posts'
path_images = 'inputs'
save_output = 'outputs/clustering/saved_images'

# Filtra apenas os arquivos .xlsx, ignorando arquivos ocultos como .DS_Store
files_to_process = [f for f in os.listdir(path_refined_clustering) if f.endswith('.xlsx')]

for file in files_to_process:
    print(f"Processando arquivo de cluster: {file}")
    # Extrai o nome base do arquivo (ex: 'full', 'lula') para usar como nome da pasta de saída.
    output_folder_name = file.replace('5. Clusterings-', '').replace('.xlsx', '')
    copy_images_to_cluster_folders(
        n=30,
        path_input_clustering=os.path.join(path_refined_clustering, file),
        path_input_normalized=os.path.join(path_normalized_posts, file.replace("5. Clusterings-", "2. Normalized-").replace(".xlsx", ".csv")),
        output_folder=output_folder_name,
        column_name=cluster_column_name,
        path_output=save_output,
    )

superEndTime = datetime.datetime.now()
superDiffTime = superEndTime - superStartTime
print("Terminou tudo em ", superEndTime)
print("Demorou total: ", superDiffTime)