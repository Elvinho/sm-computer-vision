# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob
import math

def calculate_cochran(N, confidence_level=0.95, margin_error=0.05, p=0.5):
    """
    Calcula o tamanho da amostra usando a Fórmula de Cochran para populações finitas.
    """
    if N <= 0: return 0
    
    # Z-score para 95% de confiança é aprox 1.96
    Z = 1.96 
    e = margin_error
    
    # Tamanho da amostra para população infinita (n0)
    # n0 = (Z^2 * p * (1-p)) / e^2
    n0 = (Z**2 * p * (1-p)) / (e**2)
    
    # Ajuste para população finita
    # n = n0 / (1 + ((n0 - 1) / N))
    n = n0 / (1 + ((n0 - 1) / N))
    
    return math.ceil(n)

def main():
    print("--- CÁLCULO DE AMOSTRAS (FÓRMULA DE COCHRAN) ---")
    print("Parâmetros: Confiança=95%, Margem de Erro=5%\n")
    
    base_path = os.path.join('outputs', 'clustering', 'refined')
    files = glob.glob(os.path.join(base_path, '5. Clusterings-*.xlsx'))
    
    if not files:
        print(f"Nenhum arquivo encontrado em {base_path}")
        return

    all_data = []

    for file_path in files:
        filename = os.path.basename(file_path)
        suffix = filename.replace('5. Clusterings-', '').replace('.xlsx', '')
        
        # Ignora o arquivo 'full' se quiser apenas os individuais
        if suffix == 'full': continue
        
        df = pd.read_excel(file_path)
        
        # Identifica a coluna de cluster
        cluster_col = 'Clustering_refined'
        if cluster_col not in df.columns:
            cluster_col = df.columns[-1] # Tenta a última
            
        # Conta população por cluster (N)
        # O arquivo de clusters tem uma linha por TAG. Precisamos saber quantos POSTS tem no cluster.
        # A coluna 'Posts Count' no arquivo de clusters indica quantos posts aquela tag tem, 
        # mas para saber o N do cluster, precisamos somar os posts únicos ou usar a contagem do relatório anterior.
        # O jeito mais preciso aqui é usar o count que já calculamos no generate_clustering_report.
        # Mas podemos estimar lendo o arquivo Normalized se necessário. 
        # Simplificação: Vamos usar a contagem de posts associados ao cluster (se disponível no df)
        # Como o df de clusters é por TAG, vamos ler o arquivo de posts normalizados para contar N exato.
        
        norm_file = os.path.join('outputs', 'normalize_posts', f'2. Normalized-{suffix}.csv')
        if os.path.exists(norm_file):
            df_posts = pd.read_csv(norm_file)
            # Merge para saber qual post é de qual cluster
            df_merge = pd.merge(df_posts, df[['Class', cluster_col]], on='Class', how='inner')
            # Conta posts únicos por cluster
            counts = df_merge.groupby(cluster_col)['ID'].nunique()
            
            print(f"Dataset: {suffix.upper()}")
            print(f"{'Cluster':<10} | {'População (N)':<15} | {'Amostra Cochran (n)':<20}")
            print("-" * 50)
            for cluster_id, N in counts.items():
                n = calculate_cochran(N)
                print(f"{cluster_id:<10} | {N:<15} | {n:<20}")
            print("\n")

if __name__ == "__main__":
    main()