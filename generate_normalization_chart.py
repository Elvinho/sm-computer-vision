# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def main():
    print("--- GERANDO GRÁFICO DE NORMALIZAÇÃO (ANTES vs DEPOIS) ---")
    input_path = os.path.join('outputs', 'normalize_posts', '2. Normalized-full.csv')
    output_dir = os.path.join('outputs', 'charts')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if not os.path.exists(input_path):
        print("Arquivo não encontrado. Rode o p1.py primeiro.")
        return

    df = pd.read_csv(input_path)
    # Remove duplicatas para ter uma linha por post (o arquivo original tem uma por tag)
    df_posts = df.drop_duplicates(subset=['ID'])

    # Configura o visual
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    # Cores para as redes
    palette = {'facebook': '#3b5998', 'instagram': '#E1306C'}

    # GRÁFICO 1: Antes (Curtidas Brutas)
    sns.boxplot(data=df_posts, x='Rede', y='Curtidas', ax=axes[0], palette=palette)
    axes[0].set_title('Antes: Curtidas Brutas\n(Escalas Discrepantes)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Número de Curtidas (Absoluto)')
    axes[0].set_xlabel('')
    
    # GRÁFICO 2: Depois (Normalizado)
    sns.boxplot(data=df_posts, x='Rede', y='Curtidas Normalizadas', ax=axes[1], palette=palette)
    axes[1].set_title('Depois: Engajamento Normalizado\n(Escala Padronizada 0-1)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Índice de Eficiência ($E_n$)')
    axes[1].set_xlabel('')
    axes[1].set_ylim(-0.05, 1.05) # Fixa entre 0 e 1 para mostrar o efeito

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'Grafico_Normalizacao_Comparativo.png')
    plt.savefig(save_path, dpi=300)
    print(f"-> Gráfico salvo em: {save_path}")
    print("Coloque esta imagem no slide para provar a necessidade da normalização.")

if __name__ == "__main__":
    main()
