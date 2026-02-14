# -*- coding: utf-8 -*-
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob

def main():
    print("--- GERANDO GRÁFICOS DE IMPACTO DAS TAGS (MÉDIA COM vs SEM) ---")
    
    input_dir = os.path.join('outputs', 'thesis_tables')
    output_dir = os.path.join('outputs', 'charts', 'impact_analysis')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Padrão de arquivo gerado pelo generate_frequency_analysis.py
    files = glob.glob(os.path.join(input_dir, 'Table3_Descriptive_Stats_*.xlsx'))
    
    if not files:
        print(f"[AVISO] Nenhum arquivo Table3 encontrado em {input_dir}")
        print("Certifique-se de rodar 'generate_frequency_analysis.py' primeiro.")
        return

    for file_path in files:
        filename = os.path.basename(file_path)
        # Extrai o sufixo (ex: facebook-lula)
        suffix = filename.replace('Table3_Descriptive_Stats_', '').replace('.xlsx', '')
        
        print(f"Processando: {suffix}")
        df = pd.read_excel(file_path)
        
        if df.empty:
            continue
            
        # Ordenar por Diferença de Média (Impacto)
        # Pegar Top 10 Positivos e Top 10 Negativos
        df = df.sort_values('Diferenca Media', ascending=False)
        
        top_positive = df.head(10)
        top_negative = df.tail(10)
        
        # Junta os dois para o gráfico divergente
        chart_data = pd.concat([top_positive, top_negative])
        chart_data['Tipo Impacto'] = chart_data['Diferenca Media'].apply(lambda x: 'Positivo' if x > 0 else 'Negativo')
        
        # --- GRÁFICO 1: Diverging Bar Chart (Impacto Puro) ---
        plt.figure(figsize=(12, 8))
        sns.set_theme(style="whitegrid")
        
        ax = sns.barplot(
            data=chart_data,
            x='Diferenca Media',
            y='Tag',
            hue='Tipo Impacto',
            palette={'Positivo': '#2ecc71', 'Negativo': '#e74c3c'},
            dodge=False
        )
        
        plt.title(f'Impacto das Tags no Engajamento: {suffix.upper()}', fontsize=14)
        plt.xlabel('Diferença na Média de Engajamento Normalizado (Com Tag - Sem Tag)', fontsize=12)
        plt.ylabel('Tag', fontsize=12)
        plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        
        plt.tight_layout()
        save_path = os.path.join(output_dir, f'Impacto_Divergente_{suffix}.png')
        plt.savefig(save_path, dpi=300)
        print(f"-> Salvo: {save_path}")
        plt.close()
        
        # --- GRÁFICO 2: Comparativo de Médias (Com vs Sem) ---
        # Vamos pegar apenas as Top 10 de maior impacto absoluto para focar no que importa
        df['Abs_Diff'] = df['Diferenca Media'].abs()
        top_absolute = df.sort_values('Abs_Diff', ascending=False).head(10)
        
        melted = top_absolute.melt(
            id_vars=['Tag'], 
            value_vars=['Media (Com Tag)', 'Media (Sem Tag)'],
            var_name='Condição', 
            value_name='Média de Engajamento Normalizado'
        )
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=melted, x='Média de Engajamento Normalizado', y='Tag', hue='Condição', palette='muted')
        
        plt.title(f'Comparação Direta: Com vs Sem a Tag ({suffix.upper()})', fontsize=14)
        plt.tight_layout()
        save_path2 = os.path.join(output_dir, f'Comparativo_Medias_{suffix}.png')
        plt.savefig(save_path2, dpi=300)
        print(f"-> Salvo: {save_path2}")
        plt.close()

if __name__ == "__main__":
    main()