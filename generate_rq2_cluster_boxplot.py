# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob

def main():
    print("--- GERANDO GRÁFICO RQ2: CORRELAÇÃO CLUSTER x ENGAJAMENTO ---")
    
    base_path = 'outputs'
    refined_path = os.path.join(base_path, 'clustering', 'refined')
    norm_path = os.path.join(base_path, 'normalize_posts')
    output_dir = os.path.join('outputs', 'charts')
    
    scenarios = [
        'facebook-lula', 'instagram-lula',
        'facebook-bolsonaro', 'instagram-bolsonaro'
    ]
    
    descriptions = {
        'facebook-lula': {0: 'Informativo/Texto', 1: 'Mobilização/Eventos'},
        'instagram-lula': {0: 'Carisma/Gestos', 1: 'Close/Rosto', 2: 'Ambiente', 3: 'Cidade/Multidão', 4: 'Informativo/Texto'},
        'facebook-bolsonaro': {0: 'Comício/Aglomeração', 1: 'Motociata/Veículos'},
        'instagram-bolsonaro': {0: 'Mídia/TV', 1: 'Pessoal/Formal', 2: 'Escritório/Live', 3: 'Obras/Paisagem', 4: 'Informativo/Texto'}
    }

    # Vamos gerar um gráfico separado para cada cenário para ficar legível
    for suffix in scenarios:
        # 1. Carregar Clusters
        cluster_files = glob.glob(os.path.join(refined_path, f'5. Clusterings-{suffix}.xlsx'))
        if not cluster_files: continue
        df_clusters = pd.read_excel(cluster_files[0])
        
        cluster_col = 'Clustering_refined'
        if cluster_col not in df_clusters.columns: cluster_col = df_clusters.columns[-1]

        # 2. Carregar Posts
        norm_file = os.path.join(norm_path, f'2. Normalized-{suffix}.csv')
        if not os.path.exists(norm_file): continue
        df_posts = pd.read_csv(norm_file)

        # 3. Cruzar
        df_merged = pd.merge(df_posts, df_clusters[['Class', cluster_col]], on='Class', how='inner')
        
        # Remove duplicatas de post DENTRO do mesmo cluster (mas mantém se o post estiver em clusters diferentes)
        df_plot = df_merged.drop_duplicates(subset=['ID', cluster_col])
        
        # Adiciona nomes
        df_plot['Cluster Nome'] = df_plot[cluster_col].apply(
            lambda x: descriptions.get(suffix, {}).get(x, str(x))
        )

        # 4. Plotar
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        
        # Ordenar por média para ficar bonito
        order = df_plot.groupby('Cluster Nome')['Curtidas Normalizadas'].mean().sort_values(ascending=False).index
        
        sns.boxplot(data=df_plot, x='Cluster Nome', y='Curtidas Normalizadas', order=order, palette='viridis', showfliers=False,
                    showmeans=True, meanprops={"marker":"D", "markerfacecolor":"white", "markeredgecolor":"black"})
        
        plt.title(f'RQ2: Engajamento por Cluster - {suffix.upper()}', fontsize=14)
        plt.ylabel('Engajamento Normalizado (Eficiência)', fontsize=12)
        plt.xlabel('')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        save_path = os.path.join(output_dir, f'Grafico_RQ2_Boxplot_{suffix}.png')
        plt.savefig(save_path, dpi=300)
        print(f"-> Gráfico salvo: {save_path}")

if __name__ == "__main__":
    main()
