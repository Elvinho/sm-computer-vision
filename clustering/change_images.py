
import pandas as pd
import shutil
import os
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
  column_name: str, path_output: str, names: List[str] = None, perfil: str=None
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
    qtn = n
    output_cluster = f"{output}/{names[index]}"
    # Cria o diretório de saída para o cluster, incluindo os pais, se necessário.
    os.makedirs(output_cluster, exist_ok=True)

    aux_df = posts_tags.loc[posts_tags["Class"].isin(df.loc[df[column_name] == cluster]["Class"])]
    
    if (qtn > aux_df.drop_duplicates("ID")["ID"].shape[0]):
      qtn = aux_df.drop_duplicates("ID")["ID"].shape[0]
    
    result = pd.DataFrame(columns=aux_df.columns)
    while (result['ID'].shape[0] < qtn):
      n_retiradas = qtn - result['ID'].shape[0]
      if (result.empty):
        result = aux_df.sample(n_retiradas, random_state=1).copy()
      else:
        result = pd.concat([result, aux_df.sample(n_retiradas)])
        
      result.drop_duplicates('ID', inplace=True)
      
    for post_id in result["ID"]:
      path_series = mapping_df.loc[mapping_df["ID"] == post_id]["File"]
      if not path_series.empty:
        image_path = path_series.values[0]
        shutil.copyfile(image_path, f"{output_cluster}/{post_id}.jpg")
      else:
        print(f"AVISO: Imagem para o Post ID '{post_id}' não encontrada no mapeamento. Pulando a cópia.")
    posts_tags.loc[posts_tags["ID"].isin(result["ID"])].to_csv(f"{output_cluster}/{cluster}.csv")
    posts_tags.loc[posts_tags["ID"].isin(result["ID"])].to_excel(f"{output_cluster}/{cluster}.xlsx")