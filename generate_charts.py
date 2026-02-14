# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_simple_bar(data, x, y, title, filename, output_dir, color=None, palette=None):
    plt.figure(figsize=(8, 6))
    if palette:
        ax = sns.barplot(data=data, x=x, y=y, palette=palette)
    else:
        ax = sns.barplot(data=data, x=x, y=y, color=color)
    
    plt.title(title, fontsize=14)
    plt.ylabel('Média de Engajamento Normalizado', fontsize=12)
    plt.xlabel('')
    if not data.empty and data[y].max() > 0:
        plt.ylim(0, data[y].max() * 1.15)
    
    for p in ax.patches:
        if p.get_height() > 0:
            ax.annotate(f'{p.get_height():.4f}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=10)
    
    plt.tight_layout()
    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path, dpi=300)
    print(f"-> Salvo: {save_path}")
    plt.close()

def main():
    print("--- GERANDO GRÁFICOS COMPARATIVOS ---")
    
    input_file = os.path.join('outputs', 'thesis_tables', 'Comparativo_Final_Candidatos.xlsx')
    output_dir = os.path.join('outputs', 'charts')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    if not os.path.exists(input_file):
        print(f"[ERRO] Arquivo não encontrado: {input_file}")
        print("Rode o script 'generate_candidate_comparison_table.py' primeiro.")
        return

    df = pd.read_excel(input_file)
    
    # Cria uma coluna combinada para facilitar o eixo X
    # Ex: "Lula (Instagram)"
    df['Cenario'] = df['Candidato'] + " (" + df['Rede'] + ")"
    
    # --- GRÁFICO 1: Comparação de Eficiência Máxima (Melhores Clusters) ---
    print("Gerando gráfico de Melhores Clusters...")
    
    # Pega o melhor cluster de cada cenário (o que tem maior média)
    # Como a tabela já vem ordenada, pegamos o primeiro de cada grupo 'Cenario'
    df_best = df.sort_values('Média Engajamento', ascending=False).drop_duplicates(subset=['Cenario'])
    
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    # Cria o gráfico de barras
    ax = sns.barplot(
        data=df_best, 
        x='Cenario', 
        y='Média Engajamento', 
        hue='Candidato', 
        palette={'Lula': '#c4122d', 'Bolsonaro': '#1f4e79'} # Cores sugestivas (Vermelho/Azul)
    )
    
    plt.title('Eficiência Máxima de Engajamento (Melhor Cluster por Rede)', fontsize=14)
    plt.ylabel('Média de Curtidas Normalizadas', fontsize=12)
    plt.xlabel('')
    plt.ylim(0, df_best['Média Engajamento'].max() * 1.1) # Dá um respiro no topo
    
    # Adiciona os rótulos nas barras
    for p, label in zip(ax.patches, df_best['Rótulo (Descrição)']):
        if p.get_height() > 0:
            ax.annotate(f'{p.get_height():.3f}\n({label})', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'center', 
                        xytext = (0, 20), 
                        textcoords = 'offset points',
                        fontsize=10, color='black')

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'Grafico_Eficiencia_Maxima.png')
    plt.savefig(save_path, dpi=300)
    print(f"-> Salvo: {save_path}")
    
    # --- GRÁFICO 2: Comparativo Geral das Redes (Média Ponderada) ---
    print("Gerando gráfico de Comparativo Geral das Redes...")
    # Calcula média ponderada para saber o desempenho geral da rede
    df['Weighted_Sum'] = df['Média Engajamento'] * df['N Posts']
    grouped = df.groupby(['Candidato', 'Rede'])[['Weighted_Sum', 'N Posts']].sum().reset_index()
    grouped['Média Geral'] = grouped['Weighted_Sum'] / grouped['N Posts']
    
    plt.figure(figsize=(10, 6))
    ax2 = sns.barplot(
        data=grouped,
        x='Rede',
        y='Média Geral',
        hue='Candidato',
        palette={'Lula': '#c4122d', 'Bolsonaro': '#1f4e79'}
    )
    
    plt.title('Desempenho Geral: Facebook vs Instagram', fontsize=14)
    plt.ylabel('Média de Engajamento Normalizado (Geral)', fontsize=12)
    plt.xlabel('')
    plt.ylim(0, grouped['Média Geral'].max() * 1.15)
    
    # Rótulos
    for p in ax2.patches:
        if p.get_height() > 0:
            ax2.annotate(f'{p.get_height():.3f}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontsize=10)
                        
    plt.tight_layout()
    save_path_net = os.path.join(output_dir, 'Grafico_Comparativo_Redes_Geral.png')
    plt.savefig(save_path_net, dpi=300)
    print(f"-> Salvo: {save_path_net}")

    # --- GRÁFICOS ESPECÍFICOS SOLICITADOS ---
    print("Gerando gráficos específicos (Individuais e por Rede)...")
    
    # 1. Lula: Instagram vs Facebook
    lula_data = grouped[grouped['Candidato'] == 'Lula']
    plot_simple_bar(lula_data, 'Rede', 'Média Geral', 'Desempenho Lula: Facebook vs Instagram', 'Grafico_Lula_Face_vs_Insta.png', output_dir, color='#c4122d')

    # 2. Bolsonaro: Instagram vs Facebook
    bolso_data = grouped[grouped['Candidato'] == 'Bolsonaro']
    plot_simple_bar(bolso_data, 'Rede', 'Média Geral', 'Desempenho Bolsonaro: Facebook vs Instagram', 'Grafico_Bolsonaro_Face_vs_Insta.png', output_dir, color='#1f4e79')

    # 3. Facebook: Lula vs Bolsonaro
    fb_data = grouped[grouped['Rede'] == 'Facebook']
    plot_simple_bar(fb_data, 'Candidato', 'Média Geral', 'Facebook: Lula vs Bolsonaro', 'Grafico_Facebook_Comparativo.png', output_dir, palette={'Lula': '#c4122d', 'Bolsonaro': '#1f4e79'})

    # 4. Instagram: Lula vs Bolsonaro
    insta_data = grouped[grouped['Rede'] == 'Instagram']
    plot_simple_bar(insta_data, 'Candidato', 'Média Geral', 'Instagram: Lula vs Bolsonaro', 'Grafico_Instagram_Comparativo.png', output_dir, palette={'Lula': '#c4122d', 'Bolsonaro': '#1f4e79'})

    # --- GRÁFICO 3: Matriz de Estratégia (Dispersão Melhorada) ---
    print("Gerando Matriz de Estratégia (Volume vs Eficiência)...")
    plt.figure(figsize=(12, 8))
    
    sns.scatterplot(data=df, x='N Posts', y='Média Engajamento', hue='Candidato', style='Rede', s=200, palette={'Lula': '#c4122d', 'Bolsonaro': '#1f4e79'})
    
    # Adiciona nomes aos pontos
    for i in range(df.shape[0]):
        plt.text(df['N Posts'].iloc[i]+(df['N Posts'].max()*0.02), df['Média Engajamento'].iloc[i], 
                 df['Rótulo (Descrição)'].iloc[i], horizontalalignment='left', size='small', color='black', weight='semibold')

    # Adiciona linhas médias para criar quadrantes
    plt.axvline(x=df['N Posts'].mean(), color='gray', linestyle='--', alpha=0.3)
    plt.axhline(y=df['Média Engajamento'].mean(), color='gray', linestyle='--', alpha=0.3)
    
    plt.title('Matriz de Estratégia: O que eles postam (Volume) vs O que funciona (Eficiência)', fontsize=14)
    plt.xlabel('Volume de Postagens (Quantidade)', fontsize=12)
    plt.ylabel('Eficiência (Média de Engajamento)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    save_path2 = os.path.join(output_dir, 'Grafico_Matriz_Estrategia.png')
    plt.savefig(save_path2, dpi=300)
    print(f"-> Salvo: {save_path2}")

if __name__ == "__main__":
    main()