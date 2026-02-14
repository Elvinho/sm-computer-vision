# -*- coding: utf-8 -*-
"""
Script Extra: Clusterização de Postagens (Post Clustering)
Objetivo: Agrupar POSTAGENS (não tags) e garantir que cada post tenha apenas 1 cluster.
Este script deve ser rodado APÓS o p1.py, pois utiliza os dados normalizados gerados por ele.
"""
import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans

def main():
    print("--- INICIANDO CLUSTERIZAÇÃO DE POSTAGENS (K-MEANS) ---")
    
    # 1. Carregar dados normalizados gerados pelo p1.py
    # Caminho padrão onde o p1 salva os dados limpos
    input_path = os.path.join('outputs', 'normalize_posts', '2. Normalized-full.csv')
    
    if not os.path.exists(input_path):
        print(f"Erro: Arquivo {input_path} não encontrado.")
        print("Por favor, execute o script 'social_media_visual_analysis-p1.py' primeiro.")
        return

    print(f"Lendo dados de: {input_path}")
    df = pd.read_csv(input_path)
    
    # 2. Preparar dados: Criar uma "string de tags" para cada post
    print("Agrupando tags por post...")
    # Remove espaços em tags compostas (ex: "hot dog" vira "hot_dog") para o vetorizador não separar
    df['Class_Clean'] = df['Class'].astype(str).str.replace(' ', '_')
    
    # Agrupa: Para cada ID, junta todas as tags em uma string separada por espaço
    posts_tags = df.groupby('ID')['Class_Clean'].apply(lambda x: ' '.join(x)).reset_index()
    
    # 3. Vetorização (Transformar palavras em números)
    print("Vetorizando dados...")
    # binary=True significa que só importa se a tag existe ou não (1 ou 0), não quantas vezes aparece no mesmo post
    vectorizer = CountVectorizer(binary=True)
    X = vectorizer.fit_transform(posts_tags['Class_Clean'])
    
    # 4. Clusterização (K-Means)
    k = 5 # Número de clusters desejado (pode ser alterado)
    print(f"Executando K-Means com {k} clusters...")
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X)
    
    # 5. Atribuir Cluster ao Post
    posts_tags['Cluster_Post'] = kmeans.labels_
    
    # 6. Salvar Resultado
    output_dir = os.path.join('outputs', 'clustering', 'post_clustering')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_file = os.path.join(output_dir, 'Post_Clusters.xlsx')
    
    # Recuperar metadados originais (Rede, Autor, Link) para o Excel ficar completo
    df_meta = df.drop_duplicates('ID')[['ID', 'Rede', 'Autor', 'Curtidas', 'Link', 'Data']]
    df_final = pd.merge(df_meta, posts_tags[['ID', 'Class_Clean', 'Cluster_Post']], on='ID', how='inner')
    
    df_final.to_excel(output_file, index=False)
    print(f"Sucesso! Arquivo salvo em: {output_file}")
    print("Cada post agora pertence a um único 'Cluster_Post'.")

if __name__ == "__main__":
    main()