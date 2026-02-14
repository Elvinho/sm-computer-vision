# -*- coding: utf-8 -*-
"""
Script p4: Cruzamento de dados (Merge) para Análise Comparativa.
Substitui o PROCV manual no Excel/Numbers.
"""
import pandas as pd
import os

# --- CONFIGURAÇÕES ---
# Caminhos dos arquivos gerados nas etapas anteriores
INPUT_CLUSTERING = os.path.join('outputs', 'clustering', 'refined', '5. Clusterings-full.xlsx')
INPUT_NORMALIZED = os.path.join('outputs', 'normalize_posts', '2. Normalized-full.csv')
OUTPUT_DIR = os.path.join('outputs', 'comparative_analysis')
OUTPUT_FILE = 'Comparativo_Completo.xlsx'

# Nome da coluna onde você definiu seus clusters refinados no Excel
# Se você não mudou o nome no Excel, provavelmente é "Clustering Size X" ou "Clustering_refined"
# O script tentará achar automaticamente se você deixar como None, ou você pode forçar o nome aqui.
CLUSTER_COL_NAME = "Clustering_refined" 

def main():
    print("--- Iniciando Cruzamento de Dados (p4) ---")
    
    # 1. Cria pasta de saída
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 2. Carrega os Clusters (O "Dicionário")
    if not os.path.exists(INPUT_CLUSTERING):
        print(f"[ERRO] Arquivo de clusters não encontrado: {INPUT_CLUSTERING}")
        return
    
    print(f"Lendo clusters de: {INPUT_CLUSTERING}")
    df_clusters = pd.read_excel(INPUT_CLUSTERING)
    
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
    print(f"Lendo posts de: {INPUT_NORMALIZED}")
    if os.path.exists(INPUT_NORMALIZED):
        df_posts = pd.read_csv(INPUT_NORMALIZED)
    else:
        # Tenta versão xlsx se csv não existir
        xlsx_path = INPUT_NORMALIZED.replace('.csv', '.xlsx')
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

    # 5. Limpeza e Salvamento
    # Remove duplicatas de post (se um post tiver 2 tags do mesmo cluster, não queremos contar 2x)
    df_final = df_merged.drop_duplicates(subset=['ID', target_cluster_col])
    
    # Reorganiza colunas para facilitar leitura
    cols = ['ID', 'Rede', 'Autor', 'Class', target_cluster_col, 'Curtidas', 'Curtidas Normalizadas', 'Link', 'Data']
    # Seleciona apenas as colunas que existem no dataframe final
    cols = [c for c in cols if c in df_final.columns]
    df_final = df_final[cols]

    save_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    print(f"Salvando arquivo final em: {save_path}")
    df_final.to_excel(save_path, index=False)
    
    print("\n--- SUCESSO ---")
    print(f"Agora você pode abrir o arquivo '{OUTPUT_FILE}' no Numbers/Excel.")
    print("Crie uma Tabela Dinâmica usando:")
    print(f" - Linhas: {target_cluster_col}")
    print(" - Colunas: Autor (ou Rede)")
    print(" - Valores: Contagem de ID (para frequência) ou Média de Curtidas Normalizadas (para engajamento)")

if __name__ == "__main__":
    main()
