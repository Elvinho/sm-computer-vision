# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob

def main():
    print("--- GERANDO GRÁFICO RQ1: PREDOMINÂNCIA DOS PADRÕES (VOLUME) ---")
    
    base_path = 'outputs'
    refined_path = os.path.join(base_path, 'clustering', 'refined')
    norm_path = os.path.join(base_path, 'normalize_posts')
    output_dir = os.path.join('outputs', 'charts')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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

    all_data = []

    for suffix in scenarios:
        # 1. Carregar Clusters (Tags -> Cluster)
        cluster_files = glob.glob(os.path.join(refined_path, f'5. Clusterings-{suffix}.xlsx'))
        if not cluster_files: continue
        df_clusters = pd.read_excel(cluster_files[0])
        
        cluster_col = 'Clustering_refined'
        if cluster_col not in df_clusters.columns: cluster_col = df_clusters.columns[-1]

        # 2. Carregar Posts (Post -> Tags)
        norm_file = os.path.join(norm_path, f'2. Normalized-{suffix}.csv')
        if not os.path.exists(norm_file): continue
        df_posts = pd.read_csv(norm_file)

        # 3. Cruzar para saber quais posts estão em quais clusters
        # (Um post pode estar em mais de um cluster se tiver tags de ambos)
        df_merged = pd.merge(df_posts, df_clusters[['Class', cluster_col]], on='Class', how='inner')
        
        # Conta posts únicos por cluster
        cluster_counts = df_merged.groupby(cluster_col)['ID'].nunique().reset_index()
        total_posts = df_posts['ID'].nunique()
        
        cluster_counts['Percentage'] = (cluster_counts['ID'] / total_posts) * 100
        cluster_counts['Cenario'] = suffix
        
        # Adiciona descrição
        cluster_counts['Label'] = cluster_counts[cluster_col].apply(
            lambda x: descriptions.get(suffix, {}).get(x, str(x))
        )
        
        all_data.append(cluster_counts)

    df_final = pd.concat(all_data)

    # Plotar Gráfico Facetado (Um por cenário)
    g = sns.FacetGrid(df_final, col="Cenario", col_wrap=2, sharex=False, sharey=False, height=4, aspect=1.5)
    
    def plot_bar(data, **kwargs):
        ax = plt.gca()
        sns.barplot(data=data, x='Percentage', y='Label', ax=ax, palette='viridis', orient='h')
        # Adicionar valores
        for p in ax.patches:
            width = p.get_width()
            ax.text(width + 1, p.get_y() + p.get_height()/2, f'{width:.1f}%', va='center')

    g.map_dataframe(plot_bar)
    
    g.set_titles("{col_name}")
    g.set_axis_labels("Volume de Postagens (%)", "Padrão Visual (Cluster)")
    
    plt.tight_layout()
    save_path = os.path.join(output_dir, 'Grafico_RQ1_Predominancia.png')
    plt.savefig(save_path, dpi=300)
    print(f"-> Gráfico salvo: {save_path}")

if __name__ == "__main__":
    main()
