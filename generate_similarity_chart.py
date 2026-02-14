# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def main():
    print("--- GERANDO GRÁFICO DE SIMILARIDADES (VOCABULÁRIO COMPARTILHADO) ---")
    
    base_path = 'outputs'
    norm_path = os.path.join(base_path, 'normalize_posts')
    output_dir = os.path.join('outputs', 'charts')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    scenarios = [
        {'candidato': 'Lula', 'suffix': 'facebook-lula'},
        {'candidato': 'Lula', 'suffix': 'instagram-lula'},
        {'candidato': 'Bolsonaro', 'suffix': 'facebook-bolsonaro'},
        {'candidato': 'Bolsonaro', 'suffix': 'instagram-bolsonaro'}
    ]
    
    # Definindo os "Ingredientes Comuns" (Tags representativas)
    vocabulario_comum = {
        # Expandido para incluir Close-ups (rosto) e Expressões que indicam a presença do candidato
        'Pessoal (Formal)': ['Person', 'Man', 'Spokesperson', 'Official', 'Blazer', 'Suit', 'Tie', 
                            'Smile', 'Happy', 'Chin', 'Nose', 'Eyebrow', 'Forehead', 'Human face', 'Portrait'],
        'Mobilização (Multidão)': ['Crowd', 'People', 'Event', 'Community'],
        'Informação (Texto)': ['Font', 'Text', 'Poster']
    }

    data = []

    for sc in scenarios:
        file_path = os.path.join(norm_path, f'2. Normalized-{sc["suffix"]}.csv')
        if not os.path.exists(file_path): continue
        
        df = pd.read_csv(file_path)
        # Garante posts únicos
        total_posts = df['ID'].nunique()
        
        # Para cada categoria, conta quantos posts têm pelo menos uma das tags
        for categoria, tags in vocabulario_comum.items():
            # Filtra linhas que têm essas tags
            posts_with_tags = df[df['Class'].isin(tags)]['ID'].nunique()
            pct = (posts_with_tags / total_posts) * 100
            
            data.append({
                'Candidato': sc['candidato'],
                'Rede': sc['suffix'].split('-')[0].capitalize(),
                'Elemento Visual': categoria,
                'Presença (%)': pct
            })

    df_chart = pd.DataFrame(data)

    # Plotar
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    
    # Agrupar por Elemento Visual para mostrar que ambos usam
    ax = sns.barplot(data=df_chart, x='Elemento Visual', y='Presença (%)', hue='Candidato', 
                     palette={'Lula': '#c4122d', 'Bolsonaro': '#1f4e79'})
    
    plt.title('RQ3 (Similaridades): Vocabulário Visual Compartilhado', fontsize=14)
    plt.ylabel('Presença nas Postagens (%)', fontsize=12)
    plt.xlabel('')
    plt.ylim(0, 115)
    
    # Adicionar valores
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}%',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'Grafico_RQ3_Similaridades.png')
    plt.savefig(save_path, dpi=300)
    print(f"-> Gráfico salvo: {save_path}")

if __name__ == "__main__":
    main()
