import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import shapiro
import numpy as np
import os

def mannwhitney_ts(grupo_true, grupo_false):
    statistic, p_value_mannwhitneyu = stats.mannwhitneyu(grupo_true, grupo_false, alternative='two-sided')
    return statistic, p_value_mannwhitneyu

def mannwhitney_greater(grupo_true, grupo_false):
    statistic, p_value_mannwhitneyu = stats.mannwhitneyu(grupo_true, grupo_false, alternative='greater')
    return statistic, p_value_mannwhitneyu

def mannwhitney_less(grupo_true, grupo_false):
    statistic, p_value_mannwhitneyu = stats.mannwhitneyu(grupo_true, grupo_false, alternative='less')
    return statistic, p_value_mannwhitneyu

def df_mannwhitney(df, column_target):
    result = []
    for column in df.columns[3:]:
        
        all_ids_with_tag = df[df[column] == 1]['ID'].unique()
        filter = df['ID'].isin(all_ids_with_tag)

        # filtrar o dataframe df2 original com base nos IDs que têm a tag
        group_true = df[filter][['ID', column_target]]
        group_true = group_true.drop_duplicates()
        group_true = group_true[column_target]
        
        # filtrar o daframe df2 original com base nos IDs que não têm a tag
        group_false = df[~filter][['ID', column_target]]
        group_false = group_false.drop_duplicates()
        group_false = group_false[column_target]

        stat_ts, p_value_ts = mannwhitney_ts(group_true, group_false)
        stat_greater, p_value_greater = mannwhitney_greater(group_true, group_false)
        stat_less, p_value_less = mannwhitney_less(group_true, group_false)

        # Aplicar as condições e criar a coluna 'Classification'
        statistical_classification = 'none' 
        if p_value_ts < 0.01:
            statistical_classification = 'greater' if p_value_greater < 0.01 else 'less' if p_value_less < 0.01 else 'INVALID-RESULT'

        result.append({
            'Class': column,
            'P-Value - ts': p_value_ts,
            'P-Value - greater': p_value_greater,
            'P-Value - less': p_value_less,
            'Classification': statistical_classification
        })
        
    return result

def process_files(input_folder, output_folder, column_target):

    # Listar arquivos na pasta de entrada
    files = os.listdir(input_folder)
    
    for file in files:
        # Verificar se o arquivo é CSV
        if file.endswith('.csv'):
            file_path = os.path.join(input_folder, file)
            
            # Ler o arquivo CSV
            df = pd.read_csv(file_path)
            df_reduced = df[['ID', column_target]].drop_duplicates()
            
            # Realizar o teste de Shapiro-Wilk
            stat, p_valor = stats.shapiro(df_reduced[column_target])
            
            # Exibir os resultados
            print(f'Arquivo: {file}')
            print(f'Estatística de teste: {stat:.4f}')
            print(f'Valor p: {p_valor:.9f}')

            # Interpretar o resultado
            significance = 0.05
            if p_valor > significance:
                print("Os dados parecem ser normalmente distribuídos (não rejeitamos H0)")
            else:
                df = df[[column_target, 'ID', 'Class']]
                df = df.drop_duplicates()
                dummy_categorias = pd.get_dummies(df['Class'])
                df = pd.concat([df, dummy_categorias], axis=1)
                mw = df_mannwhitney(df, column_target)
                df_mw = pd.DataFrame(mw)

                df_mw['Classification'] = 'none'
                df_mw.loc[(df_mw['P-Value - ts'] < 0.01) & (df_mw['P-Value - greater'] < 0.01), 'Classification'] = 'greater'
                df_mw.loc[(df_mw['P-Value - ts'] < 0.01) & (df_mw['P-Value - less'] < 0.01), 'Classification'] = 'less'
                
                if file.startswith('2. Normalized'):
                    new_name_file = file.replace('2. Normalized', '4. Statistical_Test-')
                if file.startswith('2. Normalized-'):
                    new_name_file = file.replace('2. Normalized-', '4. Statistical_Test-')

                # Nome do arquivo de saída baseado no arquivo de entrada
                output_file = os.path.join(output_folder, f'{new_name_file}')
                
                # Salvar o resultado no arquivo de saída
                df_mw.to_csv(output_file, index=False)
                df_mw.to_excel(output_file.replace('.csv', '.xlsx').replace('.csv', '.xlsx'), index=False)
                print(f"Resultado salvo em {output_file}/n")

def process_file_cluster(arc_cluster, arc_normalized, common_column, cluster, target, output):
    try:
        if not arc_cluster.endswith('.csv'):
            raise ValueError("O arquivo arc_cluster não possui a extensão .csv")

        df_1 = pd.read_csv(arc_cluster)
    except Exception as e:
        print(f"Erro ao ler o arquivo arc_cluster: {str(e)}")
        return

    try:
        if not arc_normalized.endswith('.csv'):
            raise ValueError("O arquivo arc_normalized não possui a extensão .csv")

        df_2 = pd.read_csv(arc_normalized)
    except Exception as e:
        print(f"Erro ao ler o arquivo arc_normalized: {str(e)}")
        return
    
    df_2 = df_2[[common_column, target, 'ID']]

    df_3 = pd.merge(df_2, df_1, on=common_column, how='left')
    df_3 = df_3.dropna()
    df_3 = df_3.drop_duplicates(subset=['ID'])
    df_3 = df_3[[common_column, cluster, target]]
    result = []

    # Realizar o teste de Shapiro-Wilk
    stat, p_valor = stats.shapiro(df_3[target])
    
    # Exibir os resultados
    print(f'Estatística de teste: {stat:.4f}')
    print(f'Valor p: {p_valor:.9f}')

    significance = 0.05
    df = pd.DataFrame()

    if p_valor > significance:
        print("Os dados parecem ser normalmente distribuídos (não rejeitamos H0)")
    else:
        clusters = df_3[cluster].unique()
        for i in clusters:
            group_true = df_3[df_3[cluster] == i][target]
            group_false = df_3[df_3[cluster] != i][target]

            stat_ts, p_value_ts = mannwhitney_ts(group_true, group_false)
            stat_greater, p_value_greater = mannwhitney_greater(group_true, group_false)
            stat_less, p_value_less = mannwhitney_less(group_true, group_false)

            # Aplicar as condições e criar a coluna 'Classification'
            statistical_classification = 'none' 
            if p_value_ts < 0.01:
                statistical_classification = 'greater' if p_value_greater < 0.01 else 'less' if p_value_less < 0.01 else 'INVALID-RESULT'

            result.append({
                'Cluster': i,
                'P-Value - ts': p_value_ts,
                'P-Value - greater': p_value_greater,
                'P-Value - less': p_value_less,
                'Classification': statistical_classification
            })
        
        df = pd.DataFrame(result)
        df['Classification'] = 'none'
        df.loc[(df['P-Value - ts'] < 0.01) & (df['P-Value - greater'] < 0.01), 'Classification'] = 'greater'
        df.loc[(df['P-Value - ts'] < 0.01) & (df['P-Value - less'] < 0.01), 'Classification'] = 'less'
        
        output_filename = f"{output}/8. Statistical_Test_Cluster-{arc_normalized.split('2. Normalized-')[-1].split('.')[0]}"

        df.to_csv(output_filename + ".csv")
        df.to_excel(output_filename + ".xlsx")


def stats_cluster_folder(folder_cluster, folder_normalized, common_column, cluster, target, output, output_clustervscluster):
    try:
        if not os.path.isdir(folder_cluster):
            raise ValueError("O caminho fornecido para folder_cluster não é um diretório válido")

        if not os.path.isdir(folder_normalized):
            raise ValueError("O caminho fornecido para folder_normalized não é um diretório válido")

        files_cluster = [f for f in os.listdir(folder_cluster) if f.endswith('.xlsx')]
        files_normalized = [f for f in os.listdir(folder_normalized) if f.endswith('.xlsx')]

        for file_cluster in files_cluster:
            for file_normalized in files_normalized:
                if ('-'.join(file_cluster.split('-')[1:])) == ('-'.join(file_normalized.split('-')[1:])):
                    df_1 = pd.read_excel(os.path.join(folder_cluster, file_cluster))
                    df_2 = pd.read_excel(os.path.join(folder_normalized, file_normalized))

                    df_2 = df_2[[common_column, target, 'ID']]

                    df_3 = pd.merge(df_2, df_1, on=common_column, how='left')
                    df_3 = df_3.dropna()

                    df_3 = df_3[['ID', common_column, cluster, target]]
                    result = []
                    result_ = []
                    clusters_visited = []

                    # Realizar o teste de Shapiro-Wilk
                    stat, p_valor = stats.shapiro(df_3[target])

                    # Exibir os resultados
                    print(f'Estatística de teste: {stat:.4f}')
                    print(f'Valor p: {p_valor:.9f}')

                    significance = 0.05
                    df = pd.DataFrame()

                    if p_valor > significance:
                        print("Os dados parecem ser normalmente distribuídos (não rejeitamos H0)")
                    else:
                        clusters = df_3[cluster].unique()

                        for i in clusters:
                            
                            all_ids_with_tag = df_3[df_3[cluster] == i]['ID'].unique()
                            filter = df_3['ID'].isin(all_ids_with_tag)

                            group_true = df_3[filter][['ID', target]]
                            group_true = group_true.drop_duplicates()
                            group_true = group_true[target]
                            
                            group_false = df_3[~filter][['ID', target]]
                            group_false = group_false.drop_duplicates()
                            group_false = group_false[target]

                            stat_ts, p_value_ts = mannwhitney_ts(group_true, group_false)
                            stat_greater, p_value_greater = mannwhitney_greater(group_true, group_false)
                            stat_less, p_value_less = mannwhitney_less(group_true, group_false)

                            # Aplicar as condições e criar a coluna 'Classification'
                            statistical_classification = 'none' 
                            if p_value_ts < 0.01:
                                statistical_classification = 'greater' if p_value_greater < 0.01 else 'less' if p_value_less < 0.01 else 'INVALID-RESULT'

                            result.append({
                                'Cluster': i,
                                'P-Value - ts': p_value_ts,
                                'P-Value - greater': p_value_greater,
                                'P-Value - less': p_value_less,
                                'Classification': statistical_classification
                            })

                            
                            for cluster_ in df_3[cluster].unique():
                                if i != cluster_ and cluster_ not in clusters_visited:
                                    all_ids_with_tag = df_3[df_3[cluster] == cluster_]['ID'].unique()
                                    filter = df_3['ID'].isin(all_ids_with_tag)

                                    group_false = df_3[filter][['ID', target]]
                                    group_false = group_false.drop_duplicates()
                                    group_false = group_false[target]

                                    stat_ts, p_value_ts = mannwhitney_ts(group_true, group_false)
                                    stat_greater, p_value_greater = mannwhitney_greater(group_true, group_false)
                                    stat_less, p_value_less = mannwhitney_less(group_true, group_false)

                                    # Aplicar as condições e criar a coluna 'Classification'
                                    statistical_classification = 'none' 
                                    if p_value_ts < 0.01:
                                        statistical_classification = 'greater' if p_value_greater < 0.01 else 'less' if p_value_less < 0.01 else 'INVALID-RESULT'

                                    result_.append({
                                        'Cluster 1': i,
                                        'Cluster 2': cluster_,
                                        'P-Value - ts': p_value_ts,
                                        'P-Value - greater': p_value_greater,
                                        'P-Value - less': p_value_less,
                                        'Classification': statistical_classification
                                    })
                            
                            clusters_visited.append(i)
                                    
                        df = pd.DataFrame(result)
                        df['Classification'] = 'none'
                        df.loc[(df['P-Value - ts'] < 0.01) & (df['P-Value - greater'] < 0.01), 'Classification'] = 'greater'
                        df.loc[(df['P-Value - ts'] < 0.01) & (df['P-Value - less'] < 0.01), 'Classification'] = 'less'

                        output_filename = f"{output}/8. Statistical_Test_Cluster-{file_normalized.split('2. Normalized-')[-1].split('.')[0]}"

                        df.to_csv(output_filename + ".csv")
                        df.to_excel(output_filename + ".xlsx")

                        df_ = pd.DataFrame(result_)
                        df_['Classification'] = 'none'
                        df_.loc[(df_['P-Value - ts'] < 0.01) & (df_['P-Value - greater'] < 0.01), 'Classification'] = 'greater'
                        df_.loc[(df_['P-Value - ts'] < 0.01) & (df_['P-Value - less'] < 0.01), 'Classification'] = 'less'

                        output_filename = f"{output_clustervscluster}/8. Statistical_Test_Cluster_Cluster-{file_normalized.split('2. Normalized-')[-1].split('.')[0]}"

                        df_.to_csv(output_filename + ".csv")
                        df_.to_excel(output_filename + ".xlsx")
    except Exception as e:
        print(f"Erro ao processar os arquivos: {str(e)}")
