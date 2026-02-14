# -*- coding: utf-8 -*-
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

def load_stats_df(base_path, suffix):
    """Carrega o dataframe de estatísticas tentando XLSX primeiro (mais seguro), depois CSV."""
    file_xlsx = os.path.join(base_path, 'statistical_tests', 'classes', f'4. Statistical_Test-{suffix}.xlsx')
    file_csv = os.path.join(base_path, 'statistical_tests', 'classes', f'4. Statistical_Test-{suffix}.csv')
    
    if os.path.exists(file_xlsx):
        return pd.read_excel(file_xlsx)
    elif os.path.exists(file_csv):
        # Tenta ler CSV padrão, se ficar tudo em 1 coluna, tenta ponto-e-vírgula
        df = pd.read_csv(file_csv)
        if len(df.columns) <= 1:
            df = pd.read_csv(file_csv, sep=';')
        return df
    return None

def get_subset_data(base_path, suffix):
    """Carrega os dados de tags e posts para um sufixo específico (ex: 'lula', 'facebook')."""
    file_pre = os.path.join(base_path, 'pre_processing', f'2. Pre-Processing-{suffix}.csv')
    file_norm = os.path.join(base_path, 'normalize_posts', f'2. Normalized-{suffix}.csv')

    if not os.path.exists(file_pre):
        return None, None

    df_tags = pd.read_csv(file_pre)
    # Remover subclass 'text' se existir
    if 'Subclass' in df_tags.columns:
        df_tags = df_tags[df_tags['Subclass'] != 'text']

    # Tenta carregar posts (CSV ou XLSX)
    df_posts = None
    file_norm_xlsx = file_norm.replace('.csv', '.xlsx')
    
    if os.path.exists(file_norm):
        df_posts = pd.read_csv(file_norm)
    elif os.path.exists(file_norm_xlsx):
        df_posts = pd.read_excel(file_norm_xlsx)

    if df_posts is not None:
        total_posts = df_posts['ID'].nunique()
        return df_tags, total_posts, df_posts
    else:
        total_posts = df_tags['ID'].nunique()
        
    return df_tags, total_posts, None

def save_thesis_table(df, name, suffix):
    """Salva um DataFrame como Excel na pasta de tabelas do TCC."""
    output_dir = os.path.join('outputs', 'thesis_tables')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = f"{name}_{suffix}.xlsx"
    filepath = os.path.join(output_dir, filename)
    df.to_excel(filepath, index=False)

def print_top_20(df_tags, total_posts, title, suffix):
    """Imprime a tabela Top 20 formatada."""
    tag_counts = df_tags['Class'].value_counts().head(20)
    
    # Create DataFrame for display/saving
    data = []
    for tag, count in tag_counts.items():
        pct = (count / total_posts) * 100
        data.append({'Tag': tag, 'N (Posts)': count, '%': pct})
    
    df_top20 = pd.DataFrame(data)
    
    print(f"\n{title}")
    print(f"{'Tag':<20} | {'Posts':<8} | {'%':<6}")
    print("-" * 40)
    for index, row in df_top20.iterrows():
        print(f"{row['Tag']:<20} | {int(row['N (Posts)']):<8} | {row['%']:.0f}%")
        
    # Save
    save_thesis_table(df_top20, "Top20_Tags", suffix)

def print_frequency_text(df_tags, total_posts):
    """Imprime o texto descritivo de frequência (buckets)."""
    tag_counts = df_tags['Class'].value_counts()
    total_unique_tags = len(tag_counts)

    c_1 = (tag_counts == 1).sum()
    c_2_10 = ((tag_counts >= 2) & (tag_counts <= 10)).sum()
    c_11_100 = ((tag_counts >= 11) & (tag_counts <= 100)).sum()
    c_100_plus = (tag_counts > 100).sum()

    print(f"\n[Texto de Frequência]")
    print(f"De {total_unique_tags} tags diferentes identificadas em {total_posts} posts:")
    print(f"- {c_1} tags ({c_1/total_unique_tags:.1%}) apareceram apenas uma vez;")
    print(f"- {c_2_10} tags ({c_2_10/total_unique_tags:.1%}) apareceram entre 2 e 10 vezes;")
    print(f"- {c_11_100} tags ({c_11_100/total_unique_tags:.1%}) apareceram entre 11 e 100 vezes;")
    print(f"- {c_100_plus} tags ({c_100_plus/total_unique_tags:.1%}) apareceram mais de 100 vezes.")

def plot_frequency_histogram(df_tags, suffix):
    """Gera um histograma da distribuição de frequência das tags."""
    tag_counts = df_tags['Class'].value_counts()
    
    # Definir os buckets conforme descrito no texto
    buckets = ['1 vez', '2-10 vezes', '11-100 vezes', '> 100 vezes']
    counts = [
        (tag_counts == 1).sum(),
        ((tag_counts >= 2) & (tag_counts <= 10)).sum(),
        ((tag_counts >= 11) & (tag_counts <= 100)).sum(),
        (tag_counts > 100).sum()
    ]
    
    # Calcular porcentagens
    total = sum(counts)
    percentages = [c / total * 100 if total > 0 else 0 for c in counts]
    
    # Criar DataFrame para plotagem
    df_plot = pd.DataFrame({
        'Frequência': buckets,
        'Quantidade': counts,
        'Porcentagem': percentages
    })
    
    # Configurar diretório de saída
    output_dir = os.path.join('outputs', 'charts', 'frequency_histograms')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Plotar
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    # Usando hue para evitar avisos de depreciação do seaborn, mas mantendo a cor variada
    ax = sns.barplot(data=df_plot, x='Frequência', y='Quantidade', hue='Frequência', palette='viridis', legend=False, order=buckets)
    
    plt.title(f'Distribuição de Frequência das Tags - {suffix}', fontsize=14)
    plt.ylabel('Número de Tags Únicas', fontsize=12)
    plt.xlabel('Frequência de Aparição nos Posts', fontsize=12)
    
    # Adicionar rótulos com contagem e porcentagem
    # Filtrar apenas patches visíveis (altura > 0) para garantir alinhamento
    visible_patches = [p for p in ax.patches if p.get_height() > 0]
    # Ordenar por coordenada x para garantir que segue a ordem do eixo x
    visible_patches.sort(key=lambda x: x.get_x())
    
    for i, p in enumerate(visible_patches):
        height = p.get_height()
        if i < len(percentages):
            ax.annotate(f'{int(height)}\n({percentages[i]:.1f}%)',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=11, color='black')
                    
    plt.tight_layout()
    filename = f"Histograma_Frequencia_{suffix}.png"
    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"-> Histograma salvo: {save_path}")

def suggest_impact_tags(df_stats, p_col):
    """Sugere tags com maior impacto positivo e negativo baseado na diferença de médias."""
    # Tenta identificar colunas de média
    mean_with_col = next((c for c in df_stats.columns if 'mean' in c.lower() and 'with' in c.lower() and 'without' not in c.lower()), None)
    mean_without_col = next((c for c in df_stats.columns if 'mean' in c.lower() and 'without' in c.lower()), None)
    
    if not mean_with_col or not mean_without_col:
        return "N/A (Colunas de média não encontradas)", "N/A (Colunas de média não encontradas)"

    # Filtra apenas significativas
    sig_df = df_stats[df_stats[p_col] < 0.01].copy()
    
    if sig_df.empty:
        return "N/A", "N/A"

    # Calcula diferença (Impacto)
    sig_df['Diff'] = sig_df[mean_with_col] - sig_df[mean_without_col]
    
    # Top Positiva
    top_pos = sig_df.sort_values('Diff', ascending=False).head(1)
    if not top_pos.empty and top_pos['Diff'].values[0] > 0:
        tag_pos = f"{top_pos['Class'].values[0]} (Diff: +{top_pos['Diff'].values[0]:.4f})"
    else:
        tag_pos = "Nenhuma tag com impacto positivo claro"

    # Top Negativa (ou menor impacto positivo)
    top_neg = sig_df.sort_values('Diff', ascending=True).head(1)
    if not top_neg.empty:
        tag_neg = f"{top_neg['Class'].values[0]} (Diff: {top_neg['Diff'].values[0]:.4f})"
    else:
        tag_neg = "N/A"
        
    return tag_pos, tag_neg

def analyze_top_100(base_path, suffix):
    """Analisa a presença de tags significativas nos Top 100 posts mais engajados."""
    print(f"\n[Análise dos Top 100 Posts Mais Engajados - {suffix}]")
    
    # 0. Carregar Tags dos Posts (Pre-Processing) para contar tags únicas
    file_pre = os.path.join(base_path, 'pre_processing', f'2. Pre-Processing-{suffix}.csv')
    if not os.path.exists(file_pre):
        print("Arquivo de tags (pre-processing) não encontrado.")
        return
        
    df_tags = pd.read_csv(file_pre)
    if 'Subclass' in df_tags.columns:
        df_tags = df_tags[df_tags['Subclass'] != 'text']
    df_tags['ID'] = df_tags['ID'].astype(str)
    
    total_unique_tags = df_tags['Class'].nunique()
    print(f"Total de tags únicas no dataset: {total_unique_tags}")

    # 1. Carregar Tags Significativas (p < 0.01)
    df_stats = load_stats_df(base_path, suffix)
    if df_stats is None:
        print("Arquivo de estatísticas não encontrado.")
        return

    # Tenta encontrar a coluna de p-valor
    p_col = next((c for c in df_stats.columns if 'p-value' in c.lower() or 'pvalue' in c.lower()), None)
    
    if not p_col:
        print("Coluna de p-valor não encontrada.")
        return
        
    sig_tags_list = df_stats[df_stats[p_col] < 0.01]['Class'].unique()
    num_sig_tags = len(sig_tags_list)
    print(f"Total de tags significativas (p < 0.01): {num_sig_tags}")
    
    if num_sig_tags == 0:
        print("Nenhuma tag significativa encontrada para análise.")
        return

    # Sugestão de tags de impacto
    tag_pos_sugg, tag_neg_sugg = suggest_impact_tags(df_stats, p_col)

    # 2. Carregar Posts Normalizados e Selecionar Top 100
    file_norm = os.path.join(base_path, 'normalize_posts', f'2. Normalized-{suffix}.csv')
    if not os.path.exists(file_norm):
        print("Arquivo normalizado não encontrado.")
        return
        
    df_posts = pd.read_csv(file_norm)
    # O arquivo normalizado tem uma linha por tag, então removemos duplicatas de ID para ter posts únicos
    df_posts_unique = df_posts.drop_duplicates(subset=['ID'])
    
    # Ordenar por engajamento (Curtidas Normalizadas)
    target_col = 'Curtidas Normalizadas'
    if target_col not in df_posts_unique.columns:
        target_col = 'Curtidas' # Fallback se não houver normalizada
    
    # Pega os Top 100
    top_100_posts = df_posts_unique.sort_values(by=target_col, ascending=False).head(100)
    top_100_ids = top_100_posts['ID'].astype(str).tolist()
    
    # Filtrar apenas as tags que pertencem aos Top 100 posts
    df_tags_top_100 = df_tags[df_tags['ID'].isin(top_100_ids)]
    
    # 4. Calcular Métricas
    # A) Quantas das tags significativas apareceram nesses posts?
    tags_present_in_top_100 = df_tags_top_100['Class'].unique()
    sig_tags_found = [tag for tag in sig_tags_list if tag in tags_present_in_top_100]
    count_sig_found = len(sig_tags_found)
    pct_sig_found = (count_sig_found / num_sig_tags) * 100
    
    print(f"Das {num_sig_tags} tags significativas, {count_sig_found} ({pct_sig_found:.1f}%) apareceram nos Top 100 posts.")
    
    # B) Quantos dos Top 100 posts contêm pelo menos uma tag significativa?
    posts_with_sig = 0
    for pid in top_100_ids:
        tags_of_post = df_tags_top_100[df_tags_top_100['ID'] == pid]['Class'].tolist()
        # Se houver interseção entre as tags do post e a lista de significativas
        if not set(tags_of_post).isdisjoint(sig_tags_list):
            posts_with_sig += 1
            
    pct_posts_with_sig = (posts_with_sig / len(top_100_ids)) * 100
    print(f"{posts_with_sig} ({pct_posts_with_sig:.1f}%) dos Top 100 posts continham pelo menos uma das tags significativas.")

    # GERAR TEXTO PRONTO
    cand_name = suffix.split('-')[1].capitalize()
    net_name = suffix.split('-')[0].capitalize()
    
    print(f"\n>>> TEXTO SUGERIDO PARA SEÇÃO 4.2 ({cand_name} - {net_name}) <<<")
    print(f"Foram identificadas {total_unique_tags} tags únicas no conjunto de dados.")
    print(f"Os testes de Mann-Whitney U identificaram {num_sig_tags} tags que exibiram uma diferença significativa (p < 0.01) nas métricas de engajamento.")
    print(f"No perfil de {cand_name} no {net_name}, {pct_sig_found:.1f}% ({count_sig_found} de {num_sig_tags}) das tags identificadas apareceram nas 100 postagens de maior engajamento.")
    print(f"Além disso, {pct_posts_with_sig:.1f}% das postagens analisadas continham pelo menos uma dessas tags.")
    print(f"Considerando o impacto positivo, destaca-se a tag {tag_pos_sugg}...")
    print(f"Considerando o impacto negativo (ou menor impacto), destaca-se a tag {tag_neg_sugg}...")

def print_stats(base_path, suffix, df_tags, total_posts, df_posts=None):
    """Imprime a análise estatística completa com contagens e médias."""
    df_stats = load_stats_df(base_path, suffix)
    if df_stats is not None:
        p_col = next((c for c in df_stats.columns if 'p-value' in c.lower() or 'pvalue' in c.lower()), None)
        
        if p_col:
            sig_tags = df_stats[df_stats[p_col] < 0.01].copy()
            
            if 'Classification' in sig_tags.columns:
                sig_tags = sig_tags.sort_values(by=['Classification', p_col])
            else:
                sig_tags = sig_tags.sort_values(p_col)

            print(f"Tags com diferença significativa (p < 0.01): {len(sig_tags)}")
            
            if not sig_tags.empty:
                # Preparar dados para a tabela detalhada
                detailed_data = []
                
                # Limita a 50 tags para não travar o terminal, mas salva todas no Excel
                tags_to_process = sig_tags['Class'].unique()
                
                for tag in tags_to_process:
                    row_stats = sig_tags[sig_tags['Class'] == tag].iloc[0]
                    classification = row_stats.get('Classification', 'N/A')
                    p_val = row_stats.get(p_col, 0)
                    
                    # Inicializa variáveis
                    count_with = 0; count_without = 0
                    mean_with = 0; mean_without = 0
                    median_with = 0; median_without = 0
                    std_with = 0; std_without = 0
                    diff_mean = 0; diff_median = 0
                    impact = 'N/A'

                    # Se temos o dataframe de posts, calculamos as estatísticas reais (Raw Likes)
                    if df_posts is not None:
                        # Garante que ID é string para comparação
                        df_posts['ID'] = df_posts['ID'].astype(str)
                        df_tags['ID'] = df_tags['ID'].astype(str)
                        
                        # Remove duplicatas de posts para contar posts únicos e não tags
                        df_posts_unique = df_posts.drop_duplicates(subset=['ID'])
                        
                        # Identifica posts com e sem a tag
                        ids_with_tag = df_tags[df_tags['Class'] == tag]['ID'].unique()
                        posts_with = df_posts_unique[df_posts_unique['ID'].isin(ids_with_tag)]
                        posts_without = df_posts_unique[~df_posts_unique['ID'].isin(ids_with_tag)]
                        
                        # Define métrica (Preferência por Curtidas Normalizadas para análise justa)
                        metric = 'Curtidas Normalizadas' if 'Curtidas Normalizadas' in df_posts.columns else 'Curtidas'
                        
                        # Calcula estatísticas
                        count_with = len(posts_with)
                        count_without = len(posts_without)
                        
                        if count_with > 0:
                            mean_with = posts_with[metric].mean()
                            median_with = posts_with[metric].median()
                            std_with = posts_with[metric].std()
                        
                        if count_without > 0:
                            mean_without = posts_without[metric].mean()
                            median_without = posts_without[metric].median()
                            std_without = posts_without[metric].std()
                        
                        diff_mean = mean_with - mean_without
                        diff_median = median_with - median_without
                        impact = 'positive' if diff_mean > 0 else 'negative'
                    
                    detailed_data.append({
                        'Tag': tag,
                        'Classificacao': classification,
                        'N (Sem Tag)': count_without, 'N (Com Tag)': count_with,
                        'Mediana (Sem Tag)': median_without, 'Mediana (Com Tag)': median_with,
                        'Media (Sem Tag)': mean_without, 'Media (Com Tag)': mean_with,
                        'Desvio P. (Sem Tag)': std_without, 'Desvio P. (Com Tag)': std_with,
                        'Diferenca Media': diff_mean, 'Diferenca Mediana': diff_median,
                        'Impacto': impact, 'P-Valor': p_val
                    })
                
                df_detailed = pd.DataFrame(detailed_data)
                
                # Exibir no terminal (colunas selecionadas para caber na tela)
                cols_terminal = ['Tag', 'N (Com Tag)', 'Media (Com Tag)', 'Diferenca Media', 'Impacto']
                print(df_detailed[cols_terminal].head(50).to_string(index=False))
                
                # Salvar tabela completa
                save_thesis_table(df_detailed, "Table3_Descriptive_Stats", suffix)
            else:
                print("Nenhuma tag com p < 0.01 encontrada.")
        else:
            print(f"Coluna de p-valor não encontrada no arquivo.")
    else:
        print(f"Arquivo de estatísticas não encontrado: {file_stats}")

def run_analysis_for_subset(base_path, candidate, network):
    suffix = f"{network}-{candidate}"
    print(f"--- RELATÓRIO: {candidate.upper()} no {network.upper()} ---")
    
    # 1. Top 20 Tags
    df_tags, total_posts, df_posts = get_subset_data(base_path, suffix)
    if df_tags is not None:
        print_frequency_text(df_tags, total_posts)
        plot_frequency_histogram(df_tags, suffix)
        print_top_20(df_tags, total_posts, f"20 tags mais usadas {network.capitalize()}", suffix)
    else:
        print(f"\n[Aviso] Dados de tags não encontrados para: {suffix}")
    
    # 2. Análise Estatística
    print(f"\nAnalise estatistica ({network.capitalize()})")
    print_stats(base_path, suffix, df_tags, total_posts, df_posts)
    
    # 3. Análise Top 100 (Seção 4.2)
    analyze_top_100(base_path, suffix)

def main():
    print("--- GERANDO RELATÓRIOS INDIVIDUAIS ---")
    base_path = 'outputs'
    
    candidates = ['lula', 'bolsonaro']
    networks = ['facebook', 'instagram']
    
    reports_dir = os.path.join('outputs', 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    for candidate in candidates:
        for network in networks:
            filename = f"Relatorio_{candidate.capitalize()}_{network.capitalize()}.txt"
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Redireciona o print para o arquivo
                original_stdout = sys.stdout
                sys.stdout = f
                try:
                    run_analysis_for_subset(base_path, candidate, network)
                finally:
                    sys.stdout = original_stdout
            
            print(f"-> Relatório salvo: {filepath}")
            
    print(f"\n[INFO] Todos os relatórios de texto estão em: {reports_dir}")
    print(f"[INFO] Tabelas Excel (Top 20 e Estatísticas) estão em: outputs/thesis_tables/")

if __name__ == "__main__":
    main()