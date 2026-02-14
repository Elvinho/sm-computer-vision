# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob
import string

def main():
    print("--- LISTAGEM DE TAGS POR CLUSTER (ORDENADAS POR FREQUÊNCIA) ---")
    
    # Caminho base onde os arquivos de clusterização refinada estão salvos
    base_path = 'outputs'
    refined_path = os.path.join(base_path, 'clustering', 'refined')
    
    # Procura todos os arquivos de clusterização refinada (exceto full)
    files = glob.glob(os.path.join(refined_path, '5. Clusterings-*.xlsx'))
    files = [f for f in files if 'full' not in f]
    
    if not files:
        print(f"[ERRO] Nenhum arquivo de clusterização refinada encontrado em: {refined_path}")
        return
    
    for file_path in files:
        filename = os.path.basename(file_path)
        suffix = filename.replace('5. Clusterings-', '').replace('.xlsx', '')
        
        print(f"\n{'='*40}")
        print(f"ANALISANDO: {suffix.upper()}")
        print(f"{'='*40}")
        
        # Gera o prefixo do código (ex: LF, LI)
        try:
            parts = suffix.split('-')
            network = parts[0][0].upper() # F ou I
            candidate = parts[1][0].upper() # L or B
            code_prefix = f"{candidate}{network}"
        except:
            code_prefix = "XX"

        df = pd.read_excel(file_path)
            
        # Identifica a coluna de cluster refinado
        cluster_col = 'Clustering_refined'
        if cluster_col not in df.columns:
            cluster_cols = [c for c in df.columns if c.startswith('Clustering Size')]
            if cluster_cols:
                cluster_col = cluster_cols[-1]
            else:
                print(f"Coluna de cluster não identificada para {suffix}.")
                continue

        # Verifica se existe coluna de contagem de posts (gerada pelo p1)
        count_col = 'Posts Count'
        if count_col not in df.columns:
             # Tenta achar alguma coluna de contagem
             count_col = next((c for c in df.columns if 'count' in c.lower()), None)

        # Agrupa tags por cluster
        clusters = sorted(df[cluster_col].unique())
        
        for cluster_id in clusters:
            cluster_df = df[df[cluster_col] == cluster_id]
            
            # Ordena por contagem se existir para mostrar as mais relevantes primeiro
            if count_col:
                cluster_df = cluster_df.sort_values(by=count_col, ascending=False)
            
            tags = cluster_df['Class'].tolist()
            
            # Gera a letra correspondente (0->A, 1->B...)
            if str(cluster_id).isdigit():
                letter = string.ascii_uppercase[int(cluster_id)]
                cluster_code = f"{code_prefix}-{letter}"
            else:
                cluster_code = f"{code_prefix}-{cluster_id}"
                
            print(f"\n>>> CLUSTER {cluster_id} (CÓDIGO: {cluster_code}) - {len(tags)} tags únicas")
            
            if count_col:
                print(f"   [Top 10 Tags mais frequentes neste cluster]")
                for _, row in cluster_df.head(10).iterrows():
                    print(f"   - {row['Class']:<20} : {int(row[count_col])} posts")
            else:
                print(", ".join(tags[:20]) + ("..." if len(tags) > 20 else ""))

if __name__ == "__main__":
    main()