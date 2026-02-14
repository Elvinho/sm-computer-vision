# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob

def main():
    print("--- GERANDO GRÁFICO RQ4: MUDANÇA DE ESTRATÉGIA (MACRO-CATEGORIAS) ---")
    
    base_path = 'outputs'
    refined_path = os.path.join(base_path, 'clustering', 'refined')
    norm_path = os.path.join(base_path, 'normalize_posts')
    output_dir = os.path.join('outputs', 'charts')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Mapeamento de Clusters para Macro-Categorias
    # Baseado nas descrições validadas anteriormente
    cluster_mapping = {
        'facebook-lula': {
            0: 'Informação',      # Informativo/Texto
            1: 'Mobilização'      # Mobilização/Eventos
        },
        'instagram-lula': {
            0: 'Imagem do Líder', # Carisma/Gestos
            1: 'Imagem do Líder', # Close/Rosto
            2: 'Contexto',        # Ambiente
            3: 'Mobilização',     # Cidade/Multidão
            4: 'Informação'       # Informativo/Texto
        },
        'facebook-bolsonaro': {
            0: 'Mobilização',     # Comício/Aglomeração
            1: 'Mobilização'      # Motociata/Veículos
        },
        'instagram-bolsonaro': {
            0: 'Imagem do Líder', # Mídia/TV
            1: 'Imagem do Líder', # Pessoal/Formal
            2: 'Contexto',        # Escritório/Live
            3: 'Contexto',        # Obras/Paisagem
            4: 'Informação'       # Informativo/Texto
        }
    }

    data_list = []

    scenarios = cluster_mapping.keys()

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
        
        total_posts = df_posts['ID'].nunique()
        
        # Mapear para Macro-Categoria diretamente no dataframe expandido
        df_merged['Macro'] = df_merged[cluster_col].apply(
            lambda x: cluster_mapping[suffix].get(x, 'Outros')
        )
        
        # Conta posts únicos por Macro-Categoria (evita dupla contagem)
        macro_counts = df_merged.groupby('Macro')['ID'].nunique().reset_index()
        macro_counts['Percentage'] = (macro_counts['ID'] / total_posts) * 100
        
        parts = suffix.split('-')
        macro_counts['Rede'] = parts[0].capitalize()
        macro_counts['Candidato'] = parts[1].capitalize()
        
        data_list.append(macro_counts)

    df_final = pd.concat(data_list)

    # Plotar
    candidatos = df_final['Candidato'].unique()
    
    for cand in candidatos:
        df_cand = df_final[df_final['Candidato'] == cand]
        
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")
        
        ax = sns.barplot(data=df_cand, x='Percentage', y='Macro', hue='Rede', palette='muted')
        
        plt.title(f'RQ4: Mudança de Estratégia Visual - {cand}', fontsize=14)
        plt.xlabel('Volume de Postagens (%)', fontsize=12)
        plt.ylabel('Eixo Temático (Macro-Categoria)', fontsize=12)
        plt.xlim(0, 115)
        
        # Anotações
        for p in ax.patches:
            width = p.get_width()
            if width > 0:
                ax.text(width + 1, p.get_y() + p.get_height()/2, f'{width:.0f}%', va='center', fontsize=10)

        plt.tight_layout()
        save_path = os.path.join(output_dir, f'Grafico_RQ4_Strategy_Shift_{cand}.png')
        plt.savefig(save_path, dpi=300)
        print(f"-> Gráfico salvo: {save_path}")

if __name__ == "__main__":
    main()
