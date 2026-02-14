
import pandas as pd
import shutil
import os
import math
from typing import List

def search_path_mapping(perfil: str="Full") -> pd.DataFrame:
  """ Digits "Full" to all """
  list_dir = os.listdir("outputs/mapping")
  if (perfil.title() != "Full"):
    list_dir = list(filter(lambda path: path.lower().find(perfil.lower()) >= 0, list_dir))
  df = pd.DataFrame()
  for path in list_dir:
    df = pd.concat([df, pd.read_csv(f"outputs/mapping/{path}")])
  df["ID"] = df["ID"].apply(str)
  return df


def copy_images_to_cluster_folders(
  n: int, path_input_clustering: str, path_input_normalized: str, output_folder: str,
  column_name: str, path_output: str, names: List[str] = None, perfil: str=None,
  use_cochran: bool = False, margin_error: float = 0.05
  ) -> None :
  
  if perfil == None:
    mapping_df = search_path_mapping()
  else:
    mapping_df = search_path_mapping(perfil)
  
  if (path_input_normalized.endswith(".xlsx")):
    posts_tags = pd.read_excel(path_input_normalized)
  else:
    posts_tags = pd.read_csv(path_input_normalized)
    
  posts_tags["ID"] = posts_tags["ID"].apply(str)
  
  if (path_input_clustering.endswith('.xlsx')):
    df = pd.read_excel(path_input_clustering)
  else:
    df = pd.read_csv(path_input_clustering)

  output = f"{path_output}/{output_folder}"

  if (names == None):
    names = [name for name in df[column_name].unique()]
  elif (len(names) < len(df[column_name].unique())):
    print("Number of incompatible clustering names")
    return False
  
  for index, cluster in enumerate(df[column_name].unique()):
    output_cluster = f"{output}/{names[index]}"
    # Cria o diretório de saída para o cluster, incluindo os pais, se necessário.
    os.makedirs(output_cluster, exist_ok=True)

    aux_df = posts_tags.loc[posts_tags["Class"].isin(df.loc[df[column_name] == cluster]["Class"])]
    
    population_size = aux_df.drop_duplicates("ID")["ID"].shape[0]
    
    if use_cochran:
        Z = 1.96 # Z-score para 95% de confiança
        p = 0.5  # Proporção para variabilidade máxima
        e = margin_error
        n0 = (Z**2 * p * (1-p)) / (e**2)
        # Fórmula de Cochran com correção para população finita
        qtn = math.ceil(n0 / (1 + ((n0 - 1) / population_size)))
        print(f"   [Cochran] Cluster '{cluster}': População {population_size} -> Amostra {qtn} (Erro={e:.0%})")
    else:
        qtn = n
    
    if (qtn > population_size):
      qtn = population_size
    
    result = pd.DataFrame(columns=aux_df.columns)
    while (result['ID'].shape[0] < qtn):
      n_retiradas = qtn - result['ID'].shape[0]
      if (result.empty):
        result = aux_df.sample(n_retiradas, random_state=1).copy()
      else:
        result = pd.concat([result, aux_df.sample(n_retiradas)])
        
      result.drop_duplicates('ID', inplace=True)
      
    for post_id in result["ID"]:
      # Tenta identificar a rede para colocar no nome do arquivo
      try:
          rede = posts_tags.loc[posts_tags["ID"] == post_id, "Rede"].values[0]
          file_prefix = f"{rede}_"
      except:
          file_prefix = ""

      path_series = mapping_df.loc[mapping_df["ID"] == post_id]["File"]
      if not path_series.empty:
        image_path = path_series.values[0]
        if os.path.exists(image_path):
          shutil.copyfile(image_path, f"{output_cluster}/{file_prefix}{post_id}.jpg")
        else:
          print(f"ERRO: Arquivo não encontrado no disco: '{image_path}'. Pulando.")
      else:
        print(f"AVISO: Imagem para o Post ID '{post_id}' não encontrada no mapeamento. Pulando a cópia.")
    posts_tags.loc[posts_tags["ID"].isin(result["ID"])].to_csv(f"{output_cluster}/{cluster}.csv")
    posts_tags.loc[posts_tags["ID"].isin(result["ID"])].to_excel(f"{output_cluster}/{cluster}.xlsx")