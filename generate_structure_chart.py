# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

def main():
    print("--- GERANDO GRÁFICO DE ESTRUTURA DE CLUSTERS (RQ1) ---")
    output_dir = os.path.join('outputs', 'charts')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Dados baseados na sua clusterização (p1.py)
    data = [
        {'Candidato': 'Lula', 'Rede': 'Facebook', 'Nº Clusters': 2, 'Tipo': 'Binária'},
        {'Candidato': 'Lula', 'Rede': 'Instagram', 'Nº Clusters': 5, 'Tipo': 'Fragmentada'},
        {'Candidato': 'Bolsonaro', 'Rede': 'Facebook', 'Nº Clusters': 2, 'Tipo': 'Binária'},
        {'Candidato': 'Bolsonaro', 'Rede': 'Instagram', 'Nº Clusters': 5, 'Tipo': 'Fragmentada'},
    ]
    df = pd.DataFrame(data)

    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    palette = {'Facebook': '#3b5998', 'Instagram': '#E1306C'}
    
    ax = sns.barplot(data=df, x='Candidato', y='Nº Clusters', hue='Rede', palette=palette)
    
    # Mover a legenda para fora do gráfico (canto superior direito externo)
    plt.legend(title='Rede', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.title('RQ1: Convergência Arquitetural (A Plataforma Molda a Estrutura)', fontsize=14)
    plt.ylabel('Número de Clusters Identificados', fontsize=12)
    plt.ylim(0, 6)
    
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            label = "Binária" if height <= 2 else "Fragmentada"
            ax.annotate(f'{int(height)}\n({label})',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    # bbox_inches='tight' garante que a legenda externa não seja cortada na imagem salva
    plt.savefig(os.path.join(output_dir, 'Grafico_RQ1_Estrutura.png'), dpi=300, bbox_inches='tight')
    print("-> Gráfico salvo: Grafico_RQ1_Estrutura.png")

if __name__ == "__main__":
    main()
