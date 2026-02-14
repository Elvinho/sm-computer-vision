# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

def main():
    print("--- GERANDO GRÁFICO DE CONCENTRAÇÃO ESTRATÉGICA (RQ3) ---")
    output_dir = os.path.join('outputs', 'charts')
    
    # Dados extraídos da sua análise Top 100
    data = [
        {'Cenario': 'Lula (Face)', 'Concentracao': 91, 'Estrategia': 'Híbrida\n(Texto+Multidão)'},
        {'Cenario': 'Bolsonaro (Face)', 'Concentracao': 97, 'Estrategia': 'Monolítica\n(Comício)'},
        {'Cenario': 'Lula (Insta)', 'Concentracao': 37, 'Estrategia': 'Distribuída\n(Texto/Carisma)'},
        {'Cenario': 'Bolsonaro (Insta)', 'Concentracao': 77, 'Estrategia': 'Concentrada\n(Entrevistas)'}
    ]
    df = pd.DataFrame(data)

    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    # Cores: Vermelho para Lula, Azul para Bolsonaro
    colors = ['#c4122d', '#1f4e79', '#c4122d', '#1f4e79']
    
    ax = sns.barplot(data=df, x='Cenario', y='Concentracao', palette=colors)
    
    plt.title('RQ3: Grau de Concentração da Estratégia (Top 100 Posts)', fontsize=14)
    plt.ylabel('% de Presença do Cluster Dominante', fontsize=12)
    plt.ylim(0, 110)
    
    for i, p in enumerate(ax.patches):
        height = p.get_height()
        ax.annotate(f'{int(height)}%\n{df.iloc[i]["Estrategia"]}',
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'Grafico_RQ3_Concentracao.png'), dpi=300)
    print("-> Gráfico salvo: Grafico_RQ3_Concentracao.png")

if __name__ == "__main__":
    main()
