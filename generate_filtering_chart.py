# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns

def main():
    print("--- GERANDO GRÁFICO DE FILTRAGEM (FUNIL) ---")
    base_path = 'outputs'
    output_dir = os.path.join('outputs', 'charts')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Obter Dados Reais
    raw_path = os.path.join(base_path, 'Google', '1. GoogleVision-full.csv')
    filtered_path = os.path.join(base_path, 'pre_processing', '2. Pre-Processing-full.csv')
    
    if os.path.exists(raw_path) and os.path.exists(filtered_path):
        print("Lendo arquivos de dados...")
        df_raw = pd.read_csv(raw_path)
        df_filtered = pd.read_csv(filtered_path)
        
        # Garante que não estamos contando a subclasse 'text' se ela ainda existir no filtrado
        if 'Subclass' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Subclass'] != 'text']
            
        vocab_raw = df_raw['Class'].nunique()
        vocab_filtered = df_filtered['Class'].nunique()
        
        # Calcula o quartil para anotação
        q1 = df_raw['Percent'].quantile(0.25)
    else:
        print("[AVISO] Arquivos de dados não encontrados. Usando valores aproximados do texto.")
        vocab_raw = 3363
        vocab_filtered = 715
        q1 = 0.74

    print(f"Vocabulário Inicial: {vocab_raw}")
    print(f"Vocabulário Final: {vocab_filtered}")
    print(f"Limiar de Corte (Q1): {q1:.2f}")

    # 2. Criar o Gráfico (Comparativo com Seta de Corte)
    stages = ['Vocabulário Bruto\n(Total)', 'Vocabulário Refinado\n(Alta Confiança)']
    values = [vocab_raw, vocab_filtered]
    
    plt.figure(figsize=(8, 6))
    sns.set_theme(style="whitegrid")
    
    # Cores: Cinza para o bruto (ruído), Verde para o refinado (dados limpos)
    colors = ['#95a5a6', '#2ecc71']
    
    bars = plt.bar(stages, values, color=colors, width=0.5)
    
    # Adicionar seta indicando o filtro
    plt.annotate('', xy=(1, values[1]), xytext=(0, values[0]),
                 arrowprops=dict(arrowstyle='->', color='#c0392b', lw=2, ls='--'))
    
    # Texto explicativo no meio da seta
    mid_x = 0.5
    mid_y = (values[0] + values[1]) / 2
    plt.text(mid_x, mid_y, f'Filtro de Confiança\n< {q1:.2f} (1º Quartil)\nRemoção de Ruído', 
             ha='center', va='center', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#c0392b", alpha=0.9),
             fontsize=10, color='#c0392b', fontweight='bold')

    # Rótulos nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (max(values)*0.02),
                 f'{int(height)} termos',
                 ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.title('Redução de Ruído no Vocabulário Visual', fontsize=14)
    plt.ylabel('Quantidade de Termos Únicos (Tags)', fontsize=12)
    plt.ylim(0, max(values) * 1.2) # Espaço extra para o texto
    
    save_path = os.path.join(output_dir, 'Grafico_Funil_Filtragem.png')
    plt.savefig(save_path, dpi=300)
    print(f"-> Gráfico salvo em: {save_path}")
    plt.close()

if __name__ == "__main__":
    main()