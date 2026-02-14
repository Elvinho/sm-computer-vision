# -*- coding: utf-8 -*-
"""
Script p4: Cruzamento de dados (Merge) para Análise Comparativa.
Substitui o PROCV manual no Excel/Numbers.
Agora processa TODOS os arquivos (Full e Individuais) encontrados na pasta refined.
"""
import pandas as pd
import os
import glob

# --- CONFIGURAÇÕES ---
# Caminhos dos arquivos gerados nas etapas anteriores
CLUSTERING_DIR = os.path.join('outputs', 'clustering', 'refined')
NORMALIZED_DIR = os.path.join('outputs', 'normalize_posts')
OUTPUT_DIR = os.path.join('outputs', 'comparative_analysis')

# Nome da coluna onde você definiu seus clusters refinados no Excel
# Se você não mudou o nome no Excel, provavelmente é "Clustering Size X" ou "Clustering_refined"
# O script tentará achar automaticamente se você deixar como None, ou você pode forçar o nome aqui.
CLUSTER_COL_NAME = "Clustering_refined" 

def process_files(cluster_path, normalized_path, output_filename):
    print(f"\nProcessando: {os.path.basename(cluster_path)}")
    
    # 2. Carrega os Clusters
    if not os.path.exists(cluster_path):
        print(f"[ERRO] Arquivo de clusters não encontrado: {cluster_path}")
        return
    
    df_clusters = pd.read_excel(cluster_path)
    
    # Verifica se a coluna de cluster existe
    if CLUSTER_COL_NAME not in df_clusters.columns:
        print(f"[AVISO] Coluna '{CLUSTER_COL_NAME}' não encontrada.")
        # Tenta pegar a última coluna do arquivo como fallback (geralmente é a refinada)
        assumed_col = df_clusters.columns[-1]
        print(f"-> Usando a coluna '{assumed_col}' como cluster.")
        target_cluster_col = assumed_col
    else:
        target_cluster_col = CLUSTER_COL_NAME

    # Seleciona apenas as colunas essenciais: A Tag (Class) e o Grupo (Cluster)
    df_clusters_clean = df_clusters[['Class', target_cluster_col]].drop_duplicates()

    # 3. Carrega os Posts (Os "Dados Brutos")
    if os.path.exists(normalized_path):
        df_posts = pd.read_csv(normalized_path)
    else:
        # Tenta versão xlsx se csv não existir
        xlsx_path = normalized_path.replace('.csv', '.xlsx')
        if os.path.exists(xlsx_path):
            df_posts = pd.read_excel(xlsx_path)
        else:
            print(f"[ERRO] Arquivo de posts normalizados não encontrado.")
            return

    # Garante que ID é string para evitar problemas
    df_posts['ID'] = df_posts['ID'].astype(str)

    # 4. O Cruzamento (O "PROCV" automático)
    print("Cruzando dados (Merge)...")
    # Unimos onde a coluna 'Class' é igual nos dois arquivos
    df_merged = pd.merge(df_posts, df_clusters_clean, on='Class', how='left')
    
    # Verifica linhas não clusterizadas
    total_rows = len(df_merged)
    clustered_rows = df_merged[target_cluster_col].count()
    missing_rows = total_rows - clustered_rows
    
    if missing_rows > 0:
        print(f"[INFO] {missing_rows} tags (de {total_rows}) não pertencem a clusters estatisticamente relevantes.")
        print("       Isso é normal. Elas serão salvas como '(Neutro)' para facilitar a análise.")
        df_merged[target_cluster_col] = df_merged[target_cluster_col].fillna("(Neutro)")

    # 5. Limpeza e Salvamento
    # Remove duplicatas de post (se um post tiver 2 tags do mesmo cluster, não queremos contar 2x)
    df_final = df_merged.drop_duplicates(subset=['ID', target_cluster_col])
    
    # Reorganiza colunas para facilitar leitura
    cols = ['ID', 'Rede', 'Autor', 'Class', target_cluster_col, 'Curtidas', 'Curtidas Normalizadas', 'Link', 'Data']
    # Seleciona apenas as colunas que existem no dataframe final
    cols = [c for c in cols if c in df_final.columns]
    df_final = df_final[cols]

    save_path = os.path.join(OUTPUT_DIR, output_filename)
    print(f"Salvando arquivo final em: {save_path}")
    df_final.to_excel(save_path, index=False)

def main():
    print("--- Iniciando Cruzamento de Dados (p4) - Todos os Arquivos ---")
    
    # 1. Cria pasta de saída
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Busca todos os arquivos de clusterização refinada
    cluster_files = glob.glob(os.path.join(CLUSTERING_DIR, '5. Clusterings-*.xlsx'))
    
    if not cluster_files:
        print(f"Nenhum arquivo encontrado em {CLUSTERING_DIR}")
        return

    for cluster_file in cluster_files:
        # Identifica o sufixo (ex: 'full', 'facebook-lula')
        filename = os.path.basename(cluster_file)
        suffix = filename.replace('5. Clusterings-', '').replace('.xlsx', '')
        
        # Monta o caminho do arquivo normalizado correspondente
        normalized_file = os.path.join(NORMALIZED_DIR, f'2. Normalized-{suffix}.csv')
        
        # Define nome de saída
        output_name = f'Comparativo_{suffix}.xlsx'
        
        process_files(cluster_file, normalized_file, output_name)
    
    print("\n--- SUCESSO ---")
    print(f"Arquivos gerados na pasta: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()