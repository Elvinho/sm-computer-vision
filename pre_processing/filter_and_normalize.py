import pandas as pd
import os
from typing import Dict, Tuple, List
import json
from sklearn.preprocessing import MinMaxScaler

def clean(df: pd.DataFrame, vision: str) -> Tuple[pd.DataFrame, pd.DataFrame]: 
  """ 
  retorno: Tuple(dataframe, texts)
  """
  # Retirando os textos que são extraidos da visão do Google 
  # Remove os labels duplicados deixando o que possue maior confiança
  df_text = pd.DataFrame(columns=df.columns)
  new_df = pd.DataFrame(columns=df.columns)
  
  if(vision == "Google"):
    df_text = df.loc[df["Subclass"] == "text"]
    new_df =  df.loc[df["Subclass"] != "text"]
  else:
    new_df = df.copy()
  new_df.loc[:,"ID"] = new_df["ID"].astype(str)
  
  new_df = new_df.sort_values("Percent").drop_duplicates(["ID", "Class"])
  
  return new_df, df_text
  
def pre_processing(
  vision: str, list_dfs: Dict[str, str], filter_data: pd.DataFrame, output_path: str, save: bool =True
  ) -> Dict[str, str]:
  """ 
    vision: Visão computacional
    list_dfs: lista com nome:caminho do arquivo
    filter_data: dataframe para filtrar IDs do
    output_path: diretório para salvar labels removidos 
  """
  # Retira o primeiro quartil
  # Limpa o Dataframe
  # Retorno:
  # Dataframe já filtrado
  info = {}
  new_list = {}
  if (output_path[-1] == "/" or output_path[-1] == "\\"):
    output_path = output_path[0:len(output_path)-1]
  for path in list_dfs.keys():
    df = pd.read_csv(list_dfs[path])
    df_clean, df_text = clean(df, vision)
    
    # Filtra os IDs com base no filter_data
    df_clean = df_clean.loc[df_clean['ID'].isin(filter_data['ID'])]
    
    info[path] = {}
    
    info[path]["Quantidade de IDs inicialmente"] = int(len(df_clean["ID"].unique()))  
    info[path]["Quantidade de labels inicialmente"] = int(df_clean.shape[0])  
    info[path]["Quantas labels unicas tinha"] = len(df_clean["Class"].unique())
    
    info[path]["Primeiro quartil"] = f"de 0 a {float(df_clean['Percent'].quantile(.25))}"
    
    # Removendo o primeiro quartil de confiança
    retiradas = df_clean.loc[df_clean["Percent"] < df_clean['Percent'].quantile(.25)]
    df_clean = df_clean.loc[df_clean["Percent"] >= df_clean['Percent'].quantile(.25)]
    
    info[path]["Primeiro quartil depois do filtro"] = f"de 0 a {df_clean['Percent'].quantile(.25)}"
    info[path]["Quantas labels unicas restaram"] = len(df_clean["Class"].unique())
    info[path]["Quantidade de labels depois"] = int(df_clean.shape[0])
    info[path]["Quantidade de Ids depois"] = int(len(df_clean["ID"].unique()))  
    
    # Salvando as tags retiradas nesse processo juntamente com os textos
    retiradas = pd.concat([retiradas, df_text])
    if (not os.path.isdir(output_path+"/labels_removed")):
      os.mkdir(output_path+"/labels_removed")
    retiradas.to_excel(f"{output_path}/labels_removed/2. {vision}Vision-removidas-{path}.xlsx", index=False)
    retiradas.to_csv(f"{output_path}/labels_removed/2. {vision}-removidas-{path}.csv", index=False)

    # Salvando informações da filtragem
    with open(f'{output_path}/info-{vision}.json', 'w') as obj:
      obj.write(json.dumps(info, indent=2))
    
    
    if(save):
      if (not os.path.isdir(output_path+"/pre_processing")):
        os.mkdir(output_path+"/pre_processing")
      df_clean.to_csv(f"{output_path}/pre_processing/2. Pre-Processing-{path}.csv", index=False)
      df_clean.to_excel(f"{output_path}/pre_processing/2. Pre-Processing-{path}.xlsx", index=False)
      new_list[path] = f'{output_path}/pre_processing/2. Pre-Processing-{path}'
      
  return new_list

def save_files(df: pd.DataFrame, output: str):
  """ Save DataFrames in csv and xlsx """
  df.to_csv(f"{output}.csv", index=False)
  df.to_excel(f"{output}.xlsx", index=False)

def normalized(path: str, column: str, perfis: List[str], redes: List[str], outputs_path)-> pd.DataFrame:
  df = pd.read_excel(path)
  df = df.rename({"ID Post": "ID"}, axis=1)
  df["ID"] = df["ID"].apply(str)
  
  if (not os.path.isdir(f"{outputs_path}/normalize_posts")):
    os.mkdir(f"{outputs_path}/normalize_posts")
  
  new_df = pd.DataFrame(columns=df.columns)
  data = pd.read_csv(os.path.join(outputs_path, "pre_processing", "2. Pre-Processing-full.csv"))
  data = data.loc[data["Subclass"] != 'text']
  data["ID"] = data["ID"].apply(str)
  
  for perfil in perfis:
    # Separando apenas o perfil
    flag_perfil = df["Autor"].apply(lambda row: row.lower().find(perfil.lower()) >= 0 )
    for rede in redes:
      # Separando perfil e rede
      flag_rede = df["Rede"].apply(lambda row: row.lower().find(rede.lower()) >= 0 )
      df_perfil_rede = df.loc[(flag_perfil) & (flag_rede)]
      
      # Normalizando a coluna especificada
      MinMax_perfil_rede = MinMaxScaler()
      df_perfil_rede.insert(
        len(df_perfil_rede.columns), f"{column} Normalizadas", 
        MinMax_perfil_rede.fit_transform(df_perfil_rede[[column]])
      )
      df_perfil_rede.loc[:, f"{column} Normalizadas"] = df_perfil_rede[f"{column} Normalizadas"].round(7)

      # Merge com as tags
      data_perfil_rede = pd.merge(df_perfil_rede, data[['ID', 'Class']], how='inner', on="ID")
      
      # Salvando a rede-perfil
      save_files(data_perfil_rede, f"{outputs_path}/normalize_posts/2. Normalized-{rede}-{perfil}")
      
      if(new_df.empty):
        new_df = df_perfil_rede
      else:
        new_df = pd.concat([new_df, df_perfil_rede])
    
    # Salvando apenas o autor
    flag_autor = new_df["Autor"].apply(lambda autor: autor.lower().find(perfil.lower()) >= 0) 
    
    data_perfil = pd.merge(new_df.loc[flag_autor], data[['ID', 'Class']], how='inner', on="ID")
    
    save_files(data_perfil, f"{outputs_path}/normalize_posts/2. Normalized-{perfil}")
    

  # Salvando cada rede
  for rede in redes:
    flag_rede = new_df["Rede"].apply(lambda row: row.lower().find(rede.lower()) >= 0 )
    
    data_rede = pd.merge(new_df.loc[flag_rede], data[['ID', 'Class']], how='inner', on="ID")
    
    save_files(data_rede, f"{outputs_path}/normalize_posts/2. Normalized-{rede}")
  
  # Salvando a tabela com todas as redes e todos os candidatos
  
  data_full = pd.merge(new_df, data[['ID', 'Class']], how='inner', on="ID")
  
  save_files(data_full, f"{outputs_path}/normalize_posts/2. Normalized-full")
  return new_df.copy()
  

def split_social_media(redes: List[str], perfis: List[str], vision: str, outputPath: str, list_dfs: Dict[str, str]) -> Dict[str, str]:
  
  df_rede = [pd.DataFrame() for x in range(len(redes))] 
  df_full = pd.DataFrame() 
  for i, key in enumerate(list_dfs.keys()):
    el = pd.read_csv(list_dfs[key])
    index = i%len(redes)
    df_rede[index] = pd.concat([el, df_rede[index]])
    df_full = pd.concat([df_full, el])
  
  save_files(df_full, f"{outputPath}/{vision}/1. GoogleVision-full")
  
  list_dfs["full"] = f"{outputPath}/{vision}/1. GoogleVision-full.csv"

  for perfil in perfis:
    list_dfs[perfil] = f"{outputPath}/{vision}/1. GoogleVision-{perfil}.csv"

  for index, rede in enumerate(redes):
    save_files(df_rede[index], f"{outputPath}/{vision}/1. GoogleVision-{rede}")
    
    list_dfs[rede] = f'{outputPath}/{vision}/1. GoogleVision-{rede}.csv'
    
  return list_dfs
