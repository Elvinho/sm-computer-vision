# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob

def main():
    print("--- ANÁLISE DE DISTRIBUIÇÃO DOS TOP 100 POSTS NOS CLUSTERS ---")
    
    base_path = 'outputs'
    refined_path = os.path.join(base_path, 'clustering', 'refined')
    norm_path = os.path.join(base_path, 'normalize_posts')
    
    scenarios = [
        'facebook-lula', 'instagram-lula',
        'facebook-bolsonaro', 'instagram-bolsonaro'
    ]
    
    # Mapeamento das descrições (Baseado no seu último script)
    # Ajuste aqui se os IDs mudaram novamente após rodar o p1
    descriptions = {
        'facebook-lula': {0: 'Informativo/Texto', 1: 'Mobilização/Eventos'},
        'instagram-lula': {0: 'Carisma/Gestos', 1: 'Close/Rosto', 2: 'Ambiente', 3: 'Cidade/Multidão', 4: 'Informativo/Texto'},
        'facebook-bolsonaro': {0: 'Comício/Aglomeração', 1: 'Motociata/Veículos'},
        'instagram-bolsonaro': {0: 'Mídia/TV', 1: 'Pessoal/Formal', 2: 'Escritório/Live', 3: 'Obras/Paisagem', 4: 'Informativo/Texto'}
    }

    summary_data = []

    for suffix in scenarios:
        print(f"\n{'='*50}")
        print(f"ANALISANDO: {suffix.upper()}")
        print(f"{'='*50}")
        
        # 1. Carregar Clusters
        # Procura o arquivo xlsx na pasta refined
        pattern = os.path.join(refined_path, f'5. Clusterings-{suffix}.xlsx')
        files = glob.glob(pattern)
        if not files:
            print(f"Arquivo de cluster não encontrado para {suffix}")
            continue
        cluster_file = files[0]
            
        df_clusters = pd.read_excel(cluster_file)
        
        # Identificar coluna de cluster
        cluster_col = 'Clustering_refined'
        if cluster_col not in df_clusters.columns:
            cluster_col = df_clusters.columns[-1]
            
        # 2. Carregar Posts Normalizados
        norm_file = os.path.join(norm_path, f'2. Normalized-{suffix}.csv')
        if not os.path.exists(norm_file):
            print(f"Arquivo normalizado não encontrado: {norm_file}")
            continue
            
        df_posts = pd.read_csv(norm_file)
        
        # 3. Selecionar Top 100 Posts Únicos
        df_unique_posts = df_posts.drop_duplicates(subset=['ID'])
        
        if 'Curtidas Normalizadas' not in df_unique_posts.columns:
            print("Coluna 'Curtidas Normalizadas' não encontrada.")
            continue
            
        top_100 = df_unique_posts.sort_values('Curtidas Normalizadas', ascending=False).head(100)
        top_100_ids = top_100['ID'].tolist()
        
        mean_top100 = top_100['Curtidas Normalizadas'].mean()
        print(f"Média de Engajamento do Top 100: {mean_top100:.4f}")
        
        # 4. Cruzar Top 100 com Clusters
        df_posts_top100 = df_posts[df_posts['ID'].isin(top_100_ids)]
        df_merged = pd.merge(df_posts_top100, df_clusters[['Class', cluster_col]], on='Class', how='inner')
        
        # Contar quantos posts únicos aparecem em cada cluster
        cluster_counts = df_merged.groupby(cluster_col)['ID'].nunique().sort_values(ascending=False)
        
        print("\nDistribuição dos Top 100 Posts por Cluster:")
        print(f"{'Cluster':<10} | {'Descrição':<20} | {'Nº Posts':<10} | {'% Top 100':<10}")
        print("-" * 60)
        
        for cluster_id, count in cluster_counts.items():
            desc = descriptions.get(suffix, {}).get(cluster_id, 'Outros')
            pct = (count / 100) * 100
            print(f"{cluster_id:<10} | {desc:<20} | {count:<10} | {pct:.0f}%")
            
        # Análise rápida
        if not cluster_counts.empty:
            top_c = cluster_counts.index[0]
            top_val = cluster_counts.iloc[0]
            print(f"\n[INSIGHT] O cluster {top_c} está presente em {top_val}% dos 100 posts de maior sucesso.")
            
            # Guardar dados para tabela resumo
            desc_dom = descriptions.get(suffix, {}).get(top_c, str(top_c))
            parts = suffix.split('-')
            summary_data.append({
                'Rede': parts[0].capitalize(),
                'Candidato': parts[1].capitalize(),
                'Média Top 100 (Teto)': mean_top100,
                'Cluster Dominante': f"{top_c} ({desc_dom})",
                'Concentração (%)': (top_val / 100)
            })

    # Salvar Tabela Resumo
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        # Ordenar
        df_summary = df_summary.sort_values(['Rede', 'Média Top 100 (Teto)'], ascending=[True, False])
        
        print("\n=== TABELA RESUMO: TETO E ESTRATÉGIA ===")
        print(df_summary.to_string(index=False, formatters={'Concentração (%)': '{:.1%}'.format, 'Média Top 100 (Teto)': '{:.4f}'.format}))
        
        out_file = os.path.join('outputs', 'thesis_tables', 'Tabela_Analise_Top100.xlsx')
        df_summary.to_excel(out_file, index=False)
        print(f"\n[SUCESSO] Tabela salva em: {out_file}")

if __name__ == "__main__":
    main()