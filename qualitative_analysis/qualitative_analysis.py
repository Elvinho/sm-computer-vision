import pandas as pd
import researchpy as repr
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os
import re

def get_dummies_df(df):
    # Codificar one-hot (get dummies) para a coluna especificada no DataFrame principal
    dummies = pd.get_dummies(df['Class'])
    dummies.columns = [f'Class_{column}' for column in dummies.columns]

    # Juntar os DataFrames codificados com o DataFrame principal
    df = pd.concat([df, dummies], axis=1)
    df.drop(columns='Class', inplace=True)

    return df


def describe_class(df, df_classification, column_target):
    columns_classes = [coluna for coluna in df.columns if coluna.startswith('Class_')]
    
    results = []

    for column_class in columns_classes:
        class_ = column_class.split('Class_')[1]  # Extrair o nome da classe

        # Verificar se a classe existe no df_classification
        if class_ in df_classification['Class'].values:
            classification = df_classification.loc[df_classification['Class'] == class_, 'Classification'].values[0]
        else:
            classification = 'Not Classified'

        all_ids_with_tag = df[df[column_class] == 1]['ID'].unique()
        
        describe_true = df[df['ID'].isin(all_ids_with_tag)][['ID', column_target]].drop_duplicates()
        describe_true_stats = describe_true[column_target].describe()

        describe_false =  df[~df['ID'].isin(all_ids_with_tag)][['ID', column_target]].drop_duplicates()
        describe_false_stats = describe_false[column_target].describe()

        results.append({
            'Tag': class_,
            'Presence': 'True',
            'Count': describe_true_stats.get('count', 0),
            'Median': describe_true_stats.get('50%', 0),
            'Mean': describe_true_stats.get('mean', 0),
            'Std': describe_true_stats.get('std', 0),
            'Min': describe_true_stats.get('min', 0),
            'Max': describe_true_stats.get('max', 0),
            'Classification': classification
        })
        
        results.append({
            'Tag': class_,
            'Presence': 'False',
            'Count': describe_false_stats.get('count', 0),
            'Median': describe_false_stats.get('50%', 0),
            'Mean': describe_false_stats.get('mean', 0),
            'Std': describe_false_stats.get('std', 0),
            'Min': describe_false_stats.get('min', 0),
            'Max': describe_false_stats.get('max', 0),
            'Classification': classification
        })

    return pd.DataFrame(results)

def save_results_class(pasta_df_class, pasta_df_comp, output_folder, column_target, significance=None):
    # Listar arquivos nas pastas
    
    files_df_class = [file for file in os.listdir(pasta_df_class) if file.endswith('.csv')]
    files_df_comp = [file for file in os.listdir(pasta_df_comp) if file.endswith('.csv')]
    
    # Extrair "nomes base" dos arquivos
    nomes_base_df_class = set(re.sub(r'^\d+\.\s?Statistical_Test-', '', file).replace('.csv', '') for file in files_df_class)
    nomes_base_df_comp = set(re.sub(r'^\d+\.\s?Normalized-', '', file).replace('.csv', '') for file in files_df_comp)

    # Encontrar nomes base comuns
    comuns_nomes_base = nomes_base_df_class & nomes_base_df_comp


    # Filtrar os dataframes
    for nome_base in comuns_nomes_base:
        # Encontrar arquivos correspondentes nas duas pastas
        arquivo_df_class = next((file for file in files_df_class if re.sub(r'^\d+\.\s?Statistical_Test-', '', file).replace('.csv', '') == nome_base), None)
        arquivo_df_comp = next((file for file in files_df_comp if re.sub(r'^\d+\.\s?Normalized-', '', file).replace('.csv', '') == nome_base), None)

        # Verificar se ambos os arquivos foram encontrados
        if arquivo_df_class and arquivo_df_comp:
            # Carregar DataFrames dos arquivos correspondentes
            df_class = pd.read_csv(os.path.join(pasta_df_class, arquivo_df_class))
            df_comp = pd.read_csv(os.path.join(pasta_df_comp, arquivo_df_comp))
            
            # Filtrar df_class com base no nível de significância da coluna 'ts'
            if significance is not None:
                df_class = df_class[df_class['P-Value - ts'] < significance]

            # Filtrar df_comp com base em df_class
            df_comp = df_comp[df_comp['Class'].isin(df_class['Class'])]
            df_class = df_class[df_class['Class'].isin(df_comp['Class'])]

            # Aplicar one-hot encoding e junção
            df_comp_encoded = get_dummies_df(df_comp)
            
            # Gerar estatísticas descritivas por classe
            describe_classes = describe_class(df_comp_encoded, df_class, column_target)
            
            # Salvar o resultado do describe_classes com o nome do arquivo inicial
            output_file_path = os.path.join(output_folder, f"{nome_base}")
            
            # Salvar o resultado do describe_classes com o nome do arquivo inicial
            output_file_path = os.path.join(output_folder, f"6. Qualitative_Analysis-{nome_base}.csv")
            describe_classes.to_csv(output_file_path)
            describe_classes.to_excel(output_file_path.replace('.csv', '.xlsx'))

            print(f"O resultado foi salvo em: {output_file_path}")                             


def describe_cluster(arc_cluster, arc_normalized, common_column, cluster, target, output):
    try:
        if not arc_cluster.endswith('.xlsx'):
            raise ValueError("O arquivo arc_cluster não possui a extensão .xlsx")

        df_1 = pd.read_excel(arc_cluster)
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

    # if arc_cluster.split('-')[-1] != arc_normalized.split('-')[-1]:
    #     print("Os finais dos arquivos de entrada não são iguais")
    #     return

    df_3 = pd.merge(df_2, df_1, on=common_column, how='left')
    df_3 = df_3.dropna()
    df_3 = df_3.drop_duplicates(subset=['ID'])

    describe_analysis = df_3.groupby(cluster)[target].describe()

    output_filename = f"{output}/7. Qualitative_Analysis-{arc_normalized.split('2. Normalized-')[-1].split('.')[0]}"

    describe_analysis.to_csv(output_filename + ".csv")
    describe_analysis.to_excel(output_filename + ".xlsx")

def describe_cluster_folder(folder_cluster, folder_normalized, common_column, cluster, target, output):
    # try:
    #     if not os.path.isdir(folder_cluster):
    #         raise ValueError("O caminho fornecido para folder_cluster não é um diretório válido")

    #     if not os.path.isdir(folder_normalized):
    #         raise ValueError("O caminho fornecido para folder_normalized não é um diretório válido")

        files_cluster = [f for f in os.listdir(folder_cluster) if f.endswith('.xlsx')]
        files_normalized = [f for f in os.listdir(folder_normalized) if f.endswith('.xlsx')]

        for file_cluster in files_cluster:
            for file_normalized in files_normalized:
                if file_cluster.split('-', 1)[1].split('.')[0] == file_normalized.split('-', 1)[1].split('.')[0]:
                    df_1 = pd.read_excel(os.path.join(folder_cluster, file_cluster))
                    df_2 = pd.read_excel(os.path.join(folder_normalized, file_normalized))

                    df_2 = df_2[[common_column, target, 'ID']]
                    
                    df_3 = pd.merge(df_2, df_1, on=common_column, how='left')
                    df_3 = df_3.dropna()
                    df_3_clusters = df_3[cluster].unique()

                    # Dicionário para armazenar as estatísticas de cada cluster
                    stats_dict = {}

                    for c in df_3_clusters:
                        all_ids_with_cluster = df_3[df_3[cluster] == c]['ID'].unique()
                        describe_true = df_3[df_3['ID'].isin(all_ids_with_cluster)][['ID', 'Curtidas Normalizadas']].drop_duplicates()
                        describe_true_stats = describe_true['Curtidas Normalizadas'].describe()
                        
                        # Adiciona as estatísticas ao dicionário, usando o nome do cluster como chave
                        stats_dict[c] = describe_true_stats

                    # Cria um DataFrame a partir do dicionário de estatísticas
                    stats_df = pd.DataFrame(stats_dict)

                    # Transpõe o DataFrame para que os clusters se tornem índices e as estatísticas se tornem colunas
                    stats_df = stats_df.T

                    # Salva o DataFrame
                    output_filename = f"{output}/7. Qualitative_Analysis-{file_normalized.split('2. Normalized-')[-1].split('.')[0]}"

                    stats_df.to_csv(output_filename + ".csv")
                    stats_df.to_excel(output_filename + ".xlsx")
                    break
    #         else:
    #             continue
    #         break
    # except Exception as e:
    #     print(f"Erro ao descrever os clusters: {str(e)}")