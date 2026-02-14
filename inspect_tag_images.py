# -*- coding: utf-8 -*-
import pandas as pd
import os
import shutil

def main():
    print("--- INSPEÇÃO VISUAL DE TAGS ---")
    tag_alvo = "Font" # A tag que o professor questionou
    print(f"Buscando amostras de imagens com a tag: {tag_alvo}")
    
    # Configurações
    base_path = 'outputs'
    input_images = 'inputs'
    output_inspection = os.path.join('outputs', 'inspection', tag_alvo)
    
    if not os.path.exists(output_inspection):
        os.makedirs(output_inspection)
        
    # Cenários para analisar (Lula Face e Insta)
    scenarios = [
        {'suffix': 'facebook-lula', 'path_img': os.path.join(input_images, 'facebook', 'lula')},
        {'suffix': 'instagram-lula', 'path_img': os.path.join(input_images, 'instagram', 'lula')}
    ]
    
    for sc in scenarios:
        suffix = sc['suffix']
        print(f"\nProcessando: {suffix}")
        
        # Ler arquivo normalizado
        file_path = os.path.join(base_path, 'normalize_posts', f'2. Normalized-{suffix}.csv')
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            continue
            
        df = pd.read_csv(file_path)
        
        # Filtrar IDs que tem a tag alvo
        ids = df[df['Class'] == tag_alvo]['ID'].astype(str).unique()
        print(f"Total de posts com '{tag_alvo}': {len(ids)}")
        
        # Salvar amostra
        save_dir = os.path.join(output_inspection, suffix)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        count = 0
        for pid in ids:
            if count >= 20: break # Baixa 20 exemplos para você olhar
            
            src = os.path.join(sc['path_img'], f"{pid}.jpg")
            dst = os.path.join(save_dir, f"{pid}.jpg")
            
            if os.path.exists(src):
                shutil.copy(src, dst)
                count += 1
        print(f"-> {count} imagens copiadas para {save_dir}")
        print("Abra essa pasta e veja: São cards? São fotos editadas? São prints?")

if __name__ == "__main__":
    main()