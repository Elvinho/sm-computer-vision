# -*- coding: utf-8 -*-
import pandas as pd
import os

def main():
    base_path = 'outputs'
    
    print("--- GERADOR DE ESTATÍSTICAS PARA O TCC ---")

    # 1. Dados Brutos (Antes do Filtro)
    # O arquivo gerado pelo p1.py antes do filtro de confiança
    raw_path = os.path.join(base_path, 'Google', '1. GoogleVision-full.csv')
    
    if os.path.exists(raw_path):
        df_raw = pd.read_csv(raw_path)
        total_tags_raw = len(df_raw)
        unique_tags_raw = df_raw['Class'].nunique()
        total_posts_raw = df_raw['ID'].nunique()
        avg_tags_raw = total_tags_raw / total_posts_raw if total_posts_raw else 0
        
        # Calcula o primeiro quartil (limiar de corte)
        q1 = df_raw['Percent'].quantile(0.25)
    else:
        print(f"[ERRO] Arquivo bruto não encontrado: {raw_path}")
        return

    # 2. Dados Filtrados (Pós Filtro de Confiança)
    # O arquivo gerado pelo p1.py após remover tags com baixa confiança
    filtered_path = os.path.join(base_path, 'pre_processing', '2. Pre-Processing-full.csv')
    
    if os.path.exists(filtered_path):
        df_filtered = pd.read_csv(filtered_path)
        # Garante que não estamos contando a subclasse 'text' se ela ainda existir
        df_filtered = df_filtered[df_filtered['Subclass'] != 'text']
        
        total_tags_filtered = len(df_filtered)
        unique_tags_filtered = df_filtered['Class'].nunique()
        # Posts que sobraram (alguns podem ter perdido todas as tags)
        total_posts_filtered = df_filtered['ID'].nunique()
        avg_tags_filtered = total_tags_filtered / total_posts_filtered if total_posts_filtered else 0
    else:
        print(f"[ERRO] Arquivo filtrado não encontrado: {filtered_path}")
        return

    # 3. Dados Consolidados por Rede/Autor
    # Usamos o arquivo normalizado para contar quantos posts de cada um existem
    norm_path = os.path.join(base_path, 'normalize_posts', '2. Normalized-full.csv')
    
    if os.path.exists(norm_path):
        df_norm = pd.read_csv(norm_path)
        # O arquivo normalizado tem uma linha por tag, então removemos duplicatas de ID para contar posts
        posts_unique = df_norm.drop_duplicates(subset=['ID'])
        
        # Contagem por Autor e Rede
        counts = posts_unique.groupby(['Autor', 'Rede']).size()
        
        # Datas (para citar o período)
        if 'Data' in posts_unique.columns:
            posts_unique['Data'] = pd.to_datetime(posts_unique['Data'], errors='coerce')
            min_date = posts_unique['Data'].min()
            max_date = posts_unique['Data'].max()
            days = (max_date - min_date).days
        else:
            days = "N/A"
            
    else:
        print(f"[ERRO] Arquivo normalizado não encontrado: {norm_path}")
        return

    print("\n=== COPIE E ADAPTE O TEXTO ABAIXO PARA SEUS RESULTADOS ===\n")
    
    print(f"Os experimentos foram realizados de acordo com a metodologia apresentada na Seção 3.")
    print(f"A coleta de dados abrangeu um período de {days} dias (de {min_date.strftime('%d/%m/%Y')} a {max_date.strftime('%d/%m/%Y')})")
    print(f"e reuniu um total de {len(posts_unique)} publicações analisadas.")
    print("\nDetalhamento por perfil:")
    print(counts.to_string())
    print(f"\nEssas publicações receberam inicialmente um total de {total_tags_raw} marcações (tags) via Google Vision API,")
    print(f"com uma média de {avg_tags_raw:.1f} marcações cada, provenientes de um vocabulário de {unique_tags_raw} termos únicos.")
    print(f"\nNo pré-processamento, filtramos todas as marcações com confiança inferior a {q1:.2f} (1º quartil),")
    print(f"reduzindo o número total de marcações para {total_tags_filtered} e o vocabulário para {unique_tags_filtered} termos únicos,")
    print(f"resultando em uma média ajustada de {avg_tags_filtered:.1f} marcações por publicação.")
    print("\n============================================================")

if __name__ == "__main__":
    main()