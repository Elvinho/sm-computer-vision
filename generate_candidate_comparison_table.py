# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob

def main():
    print("--- GERANDO TABELA COMPARATIVA DE CLUSTERS (LULA vs BOLSONARO) ---")
    
    base_path = os.path.join('outputs', 'qualitative_analysis', 'clusters')
    output_dir = os.path.join('outputs', 'thesis_tables')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    scenarios = [
        {'cand': 'Lula', 'net': 'Facebook', 'suffix': 'facebook-lula'},
        {'cand': 'Lula', 'net': 'Instagram', 'suffix': 'instagram-lula'},
        {'cand': 'Bolsonaro', 'net': 'Facebook', 'suffix': 'facebook-bolsonaro'},
        {'cand': 'Bolsonaro', 'net': 'Instagram', 'suffix': 'instagram-bolsonaro'},
    ]
    
    # Mapeamento das descrições conforme seu texto
    descriptions = {
        'facebook-lula': {0: 'Informativo/Texto', 1: 'Mobilização/Eventos'},
        'instagram-lula': {0: 'Carisma/Gestos', 1: 'Close/Rosto', 2: 'Ambiente', 3: 'Cidade/Multidão', 4: 'Informativo/Texto'},
        'facebook-bolsonaro': {0: 'Comício/Aglomeração', 1: 'Motociata/Veículos'},
        'instagram-bolsonaro': {0: 'Mídia/TV', 1: 'Pessoal/Formal', 2: 'Escritório/Live', 3: 'Obras/Paisagem', 4: 'Informativo/Texto'}
    }
    
    master_data = []
    
    for sc in scenarios:
        suffix = sc['suffix']
        # Procura o arquivo xlsx
        pattern = os.path.join(base_path, f"*{suffix}*")
        files = glob.glob(pattern)
        
        if not files:
            print(f"[AVISO] Arquivo não encontrado para {suffix}")
            continue
            
        # Tenta carregar as tags para ajudar na conferência dos IDs
        tags_file = os.path.join('outputs', 'clustering', 'refined', f'5. Clusterings-{suffix}.xlsx')
        top_tags_map = {}
        if os.path.exists(tags_file):
            try:
                df_tags = pd.read_excel(tags_file)
                if 'Clustering_refined' in df_tags.columns and 'Posts Count' in df_tags.columns:
                    for c_id in df_tags['Clustering_refined'].unique():
                        tags = df_tags[df_tags['Clustering_refined'] == c_id].sort_values('Posts Count', ascending=False).head(5)['Class'].tolist()
                        top_tags_map[c_id] = ", ".join(tags)
            except:
                pass
            
        # Prioriza xlsx
        file_path = next((f for f in files if f.endswith('.xlsx')), files[0])
        
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
                
            # Normaliza colunas
            cols = df.columns
            cluster_col = cols[0] # Assume que a primeira coluna é o ID do cluster
            
            # Encontra colunas de estatística
            mean_col = next((c for c in cols if 'mean' in c.lower()), None)
            count_col = next((c for c in cols if 'count' in c.lower()), None)
            std_col = next((c for c in cols if 'std' in c.lower()), None)
            
            if mean_col and count_col:
                for _, row in df.iterrows():
                    cluster_id = row[cluster_col]
                    # Pega a descrição do dicionário ou deixa em branco
                    desc = descriptions.get(suffix, {}).get(cluster_id, 'Outros')
                    
                    # Imprime para conferência
                    tags_preview = top_tags_map.get(cluster_id, "N/A")
                    print(f"  [{suffix}] Cluster {cluster_id}: {desc} | Tags: {tags_preview}")
                    
                    master_data.append({
                        'Candidato': sc['cand'],
                        'Rede': sc['net'],
                        'Cluster ID': cluster_id,
                        'Rótulo (Descrição)': desc,
                        'N Posts': row[count_col],
                        'Média Engajamento': row[mean_col],
                        'Desvio Padrão': row[std_col] if std_col else 0
                    })
        except Exception as e:
            print(f"[ERRO] Falha ao ler {file_path}: {e}")

    if master_data:
        df_final = pd.DataFrame(master_data)
        # Ordena por Rede e depois pela Média (do maior para o menor) para facilitar comparação
        df_final = df_final.sort_values(by=['Rede', 'Média Engajamento'], ascending=[True, False])
        
        out_file = os.path.join(output_dir, 'Comparativo_Final_Candidatos.xlsx')
        df_final.to_excel(out_file, index=False)
        print(f"\n[SUCESSO] Tabela gerada em: {out_file}")
        print("Use este arquivo para criar os gráficos comparativos no Excel.")

if __name__ == "__main__":
    main()