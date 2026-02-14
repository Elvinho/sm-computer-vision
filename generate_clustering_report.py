# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob
import string

def generate_report_for_suffix(suffix):
    print(f"\n{'='*50}")
    print(f"RELATÓRIO DE CLUSTERIZAÇÃO: {suffix.upper()}")
    print(f"{'='*50}")
    
    # Caminho base onde o p3.py salvou a análise qualitativa
    base_path = 'outputs'
    qual_path = os.path.join(base_path, 'qualitative_analysis', 'clusters')
    
    # Procura o arquivo de análise para o sufixo
    files = glob.glob(os.path.join(qual_path, f'*{suffix}*'))
    if not files:
        print(f"[AVISO] Arquivo de análise qualitativa não encontrado para '{suffix}' em: {qual_path}")
        return
    
    # Prioriza .xlsx
    file_path = next((f for f in files if f.endswith('.xlsx')), files[0])
    print(f"Lendo dados de: {file_path}")
    
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
        
    # Identifica colunas
    cluster_col = df.columns[0] # Geralmente a primeira é o nome do Cluster
    
    # Se a primeira coluna for "Unnamed", renomeia para "Cluster"
    if "Unnamed" in str(cluster_col):
        df.rename(columns={cluster_col: 'Cluster'}, inplace=True)
        cluster_col = 'Cluster'

    mean_col = next((c for c in df.columns if 'mean' in c.lower()), None)
    median_col = next((c for c in df.columns if '50%' in c or 'median' in c.lower()), None)
    std_col = next((c for c in df.columns if 'std' in c.lower()), None)
    count_col = next((c for c in df.columns if 'count' in c.lower()), None)
    
    if not mean_col:
        print("Colunas de estatística não identificadas.")
        return

    # Análises
    num_clusters = len(df)
    best_cluster = df.sort_values(by=mean_col, ascending=False).iloc[0]
    worst_cluster = df.sort_values(by=mean_col, ascending=True).iloc[0]
    stable_cluster = df.sort_values(by=std_col, ascending=True).iloc[0] if std_col else None
    
    print(f"\n=== DADOS PARA O TEXTO ({suffix}) ===")
    print(f"Número de Clusters: {num_clusters}")
    print(f"Melhor Cluster (Maior Média): {best_cluster[cluster_col]} (Média: {best_cluster[mean_col]:.4f})")
    print(f"Pior Cluster (Menor Média): {worst_cluster[cluster_col]} (Média: {worst_cluster[mean_col]:.4f})")
    
    if stable_cluster is not None:
        print(f"Cluster Mais Estável (Menor Std): {stable_cluster[cluster_col]} (Std: {stable_cluster[std_col]:.4f})")
    
    # --- GERAÇÃO DA TABELA PARA O TCC (Com Nomenclatura LF-A, LI-B...) ---
    # Define o prefixo baseado no sufixo (ex: facebook-lula -> LF)
    parts = suffix.split('-')
    network = parts[0][0].upper() # F ou I
    candidate = parts[1][0].upper() # L or B
    # Ordem pedida: Candidato + Rede (ex: Lula Face = LF)
    code_prefix = f"{candidate}{network}"
    
    # Cria mapeamento de números para letras (0->A, 1->B...)
    # Assume que os clusters são 0, 1, 2...
    df['Código'] = df[cluster_col].apply(lambda x: f"{code_prefix}-{string.ascii_uppercase[int(x)]}" if str(x).isdigit() else str(x))
    
    print(f"\n=== TABELA RESUMO: {suffix} ===")
    cols_to_show = ['Código', count_col, mean_col, std_col]
    cols_to_show = [c for c in cols_to_show if c]
    
    # Renomear colunas para ficar bonito no TCC
    rename_map = {
        count_col: 'Nº Postagens',
        mean_col: 'Média Engajamento',
        std_col: 'Desvio Padrão'
    }
    df_display = df[cols_to_show].rename(columns=rename_map)
    
    # Formata para exibição
    print(df_display.to_string(index=False))
    
    # Salvar tabela formatada
    output_dir = os.path.join('outputs', 'thesis_tables')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_path = os.path.join(output_dir, f'Tabela_Clusters_{suffix}.xlsx')
    df_display.to_excel(save_path, index=False)
    print(f"\n[SUCESSO] Tabela salva em: {save_path}")

def main():
    # Lista de sufixos para analisar
    suffixes = [
        'facebook-lula',
        'instagram-lula',
        'facebook-bolsonaro',
        'instagram-bolsonaro'
    ]
    
    print("Iniciando geração de relatórios individuais de clusterização...")
    
    for suffix in suffixes:
        generate_report_for_suffix(suffix)
        
    print("\n[INFO] Se algum relatório estiver faltando, verifique se rodou o script p3.py para todos os casos.")

if __name__ == "__main__":
    main()