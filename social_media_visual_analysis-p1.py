# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 08:49:14 2024

@author: Kellyton Brito
"""

# Bibliotecas
import pandas as pd
import os
import datetime

# Modulos
from computer_vision.tagging import create_file_id, send_imagens_API
from pre_processing.filter_and_normalize import pre_processing, normalized, split_social_media
from word_cloud.generate import create_wordcloud
from statistical_tests.statistical_tests import *
from qualitative_analysis.qualitative_analysis import *
from clustering.overlap_clustering import clusterize_tags


#Configurações de entrada e de redes
perfis = [
  "lula",
  "bolsonaro",
]

arrobas = [
  "@lulaoficial",
  "@bolsonaromessiasjair",
]

redes = [
  "facebook",
  "instagram"
]

path_metadados = "inputs/Posts_Ajustado_tiktok_face_insta.xlsx"
path_diferenca = "inputs/Posts_sem_fotos.xlsx"

inputPath = "inputs"
outputPath = "outputs"

vision = "Google"
#vision = "Amazon"

# Defina como True para enviar imagens para a API do Google Vision.
# Defina como False para pular o envio e usar os resultados existentes (modo de reanálise).
RUN_VISION_API = False
# significance = 0.01

"""
Premissas: já tem ter pastas com as imagens no padrão: rede/candidato
Tem que ter uma planilha de metadados com o cabeçalho:
ID Post	Autor	Data	Texto	Link	Rede	Tipo	Curtidas	Comentários	Compart.
Exemplo: Posts_Ajustado_tiktok_face_insta.xlsx

Tem que ter outra ("Posts_sem_fotos.xlsx") pra ele retirar da primeria
"""
#Passo 1: Tagging
#Entrada: Arquivos de imagens e planilha de metadados
#Saída: Planilha de 2 colunas linkando o ID do post e o arquivo(caminho) correspondente

superStartTime = datetime.datetime.now()
print("Comecou tudo em ", superStartTime)

list_dfs = {}

METADATA = pd.read_excel(path_metadados)
METADATA.loc[:,"ID Post"] = METADATA["ID Post"].astype(str)
DIFERENCA = pd.read_excel(path_diferenca)
DIFERENCA.loc[:,"ID"] = DIFERENCA["ID"].astype(str)

data_filter = METADATA.loc[~METADATA['ID Post'].isin(DIFERENCA.loc[DIFERENCA['link funciona'] != 1]['ID'])]
data_filter = data_filter.rename({"ID Post": 'ID'}, axis=1)
data_filter.loc[:,"ID"] = data_filter["ID"].astype(str)
 

# Cria pasta de saida caso não esteja criada
if(not os.path.isdir(outputPath)):
  os.mkdir(outputPath)
    
for index, perfil in enumerate(perfis):
  df_perfil = pd.DataFrame()
  for rede in redes:
    
    # Mapeamento criando uma planilha com o ID e local das imagens
    if(not os.path.isdir(f'{outputPath}/mapping')):
      os.mkdir(f'{outputPath}/mapping')

    mapping_file_csv=f"{outputPath}/mapping/1. Mapping-File-id-{rede}-{perfil}.csv"
    create_file_id(f"{inputPath}/{rede}/{perfil}", mapping_file_csv, arrobas[index])
    
    # Enviar para a visão computacional gerar as tags
    # 1 = Google, 2 é Amazon. Não está funcionando o da Amazon, só de de Gaby funciona
    send_imagens_API(
      mapping_file_csv,
      vision=1,
      path_vision=f'{outputPath}/{vision}/1. GoogleVision-{rede}-{perfil}',
      metadada=data_filter,
      fake = not RUN_VISION_API
    )
    
    list_dfs[f"{rede}-{perfil}"] = f'{outputPath}/{vision}/1. GoogleVision-{rede}-{perfil}.csv'
    
    # Separando perfil automaticamente
    df_perfil = pd.concat([pd.read_csv(f'{outputPath}/{vision}/1. GoogleVision-{rede}-{perfil}.csv'), df_perfil])

  
  df_perfil.to_excel(f"{outputPath}/{vision}/1. GoogleVision-{perfil}.xlsx", index=False)
  df_perfil.to_csv(f"{outputPath}/{vision}/1. GoogleVision-{perfil}.csv", index=False)

# Separando os Datasets por redes e em full( todos os candidatos e redes)
split_social_media(
  redes=redes, 
  perfis=perfis, 
  vision=vision, 
  outputPath=outputPath, 
  list_dfs=list_dfs
  ) 
# Pre-processamento das labels

""" 
Precisa da visão computacional 'Google' ou 'Amazon'
list_dfs: dicionário com chave = 'perfil-rede' e valor o caminho para o arquivo
filter_data: faz um segunda verificação sobre os IDs imagens
output_path: onde os arquivos serão gerados
"""


list_dfs_filter = pre_processing(
  vision=vision, 
  list_dfs=list_dfs, 
  filter_data=data_filter, 
  output_path=outputPath,
  ) 


# Normalizando dados
normalized(
  path= "inputs/Post-filtrado.xlsx",
  column= "Curtidas",
  perfis= perfis,
  redes= redes,
  outputs_path= 'outputs'
)


for path_df in list_dfs_filter.keys():
  df = pd.read_csv(list_dfs_filter[path_df]+".csv")
  #Criando a nuvem de palavras
  create_wordcloud(
    df=df, 
    path=path_df, 
    output=outputPath
  )


path_normalized = f'{outputPath}/normalize_posts'
path_results_statistical = f'{outputPath}/statistical_tests/classes'
path_results_qualitative = f'{outputPath}/qualitative_analysis/classes'

if (not os.path.isdir(path_results_statistical)):
  os.mkdir(path_results_statistical)
  
if (not os.path.isdir(path_results_qualitative)):
  os.mkdir(path_results_qualitative)
  
# column_target = 'Curtidas Normalizadas'
column_target = 'Curtidas'

# From the normalized data, we will store the values of the Mann-Whitney statistical test, 
# according to the desired column, in the current case: 'Curtidas Normalizadas'.
process_files(path_normalized, path_results_statistical, column_target)
save_results_class(pasta_df_class=path_results_statistical, pasta_df_comp=path_normalized, output_folder=path_results_qualitative, column_target=column_target)

# Cria várias opções de clusterizações das tags com diferentes quantidades de "grupos"
# São escolhidas as "top_n_clusterings" quantidades de maior sillhouette score
# Também são geradas arquivos dos gráficos dos sillhouette scores para cada quantidade de grupos considerada
paths_statisticals = os.listdir(path_results_statistical)
paths_statisticals = [ path.replace("4. Statistical_Test-", "") for path in filter(lambda path: path.find(".csv") >= 0, paths_statisticals)]

for file in paths_statisticals:
    clusterize_tags(f"{outputPath}/statistical_tests/classes/4. Statistical_Test-{file}", 
                    f"{outputPath}/normalize_posts/2. Normalized-{file}",
                    f"{outputPath}/clustering/", 
                    f"{file}",
                    top_n_clusterings=3)


# Depois da clusterização: fazer análise manual dos clusters
# Ler "clustering_howto.md" para mais detalhes

superEndTime = datetime.datetime.now()
superDiffTime = superEndTime - superStartTime
print("Terminou tudo em ", superEndTime)
print("Demorou total: ", superDiffTime)
