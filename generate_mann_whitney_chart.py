# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from scipy.stats import mannwhitneyu

def main():
    print("--- GERANDO GRÁFICO DE VALIDAÇÃO ESTATÍSTICA COMPARATIVO (RQ2) ---")
    output_dir = os.path.join('outputs', 'charts')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Configuração dos cenários para comparação
    # Usamos 'Crowd' para ambos pois é a tag técnica para Multidão/Aglomeração
    scenarios = [
        {
            'candidato': 'Lula',
            'file_suffix': 'facebook-lula',
            'tag': 'Crowd',
            'label_pt': 'Aglomeração'
        },
        {
            'candidato': 'Bolsonaro',
            'file_suffix': 'facebook-bolsonaro',
            'tag': 'Crowd',
            'label_pt': 'Aglomeração'
        }
    ]

    # Cria figura com 2 subplots lado a lado
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    sns.set_theme(style="whitegrid")

    for i, sc in enumerate(scenarios):
        file_path = os.path.join('outputs', 'normalize_posts', f'2. Normalized-{sc["file_suffix"]}.csv')
        
        if not os.path.exists(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            continue

        df = pd.read_csv(file_path)
        target_tag = sc['tag']
        
        # Identificar IDs que têm a tag
        ids_with = df[df['Class'] == target_tag]['ID'].unique()
        
        # Criar DataFrame único por post (removendo duplicatas de tags)
        df_posts = df.drop_duplicates(subset=['ID']).copy()
        
        # Criar coluna de grupo
        df_posts['Grupo'] = df_posts['ID'].apply(lambda x: 'Com Tag' if x in ids_with else 'Sem Tag')
        
        # Calcular Estatística
        group_with = df_posts[df_posts['ID'].isin(ids_with)]['Curtidas Normalizadas']
        group_without = df_posts[~df_posts['ID'].isin(ids_with)]['Curtidas Normalizadas']
        
        stat, p_value = mannwhitneyu(group_with, group_without, alternative='two-sided')
        
        print(f"[{sc['candidato']}] Tag: {target_tag} | P-Valor: {p_value}")

        # Plotar no eixo correspondente
        ax = axes[i]
        palette = {'Sem Tag': '#95a5a6', 'Com Tag': '#2ecc71'}
        
        sns.boxplot(data=df_posts, x='Grupo', y='Curtidas Normalizadas', ax=ax, palette=palette, showfliers=False,
                    showmeans=True, meanprops={"marker":"D", "markerfacecolor":"white", "markeredgecolor":"black", "markersize":"8"})
        
        # Adicionar anotação do P-Valor
        y_max = df_posts['Curtidas Normalizadas'].quantile(0.95)
        x1, x2 = 0, 1
        y, h = y_max + 0.05, 0.02
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c='black')
        
        p_text = "$p < 0.01$" if p_value < 0.01 else f"$p = {p_value:.3f}$"
        ax.text((x1+x2)*.5, y+h, f"\n{p_text}", ha='center', va='bottom', color='black', fontweight='bold')

        ax.set_title(f"{sc['candidato']} (Facebook)\nTag: '{target_tag}' ({sc['label_pt']})", fontsize=14)
        ax.set_xlabel('')
        
        if i == 0:
            ax.set_ylabel('Engajamento Normalizado (Eficiência)', fontsize=12)
        else:
            ax.set_ylabel('') # Remove label do segundo gráfico para limpar
    
    plt.tight_layout()
    save_path = os.path.join(output_dir, 'Grafico_Validacao_Estatistica_Comparativo.png')
    plt.savefig(save_path, dpi=300)
    print(f"-> Gráfico salvo em: {save_path}")
    print("Use este gráfico no Slide de Testes Estatísticos (RQ2).")

if __name__ == "__main__":
    main()
