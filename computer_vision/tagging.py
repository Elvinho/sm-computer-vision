import os
import pandas as pd
from typing import List
# from computer_vision.google_vision import load_labels # Import para o código antigo
from computer_vision.google_vision import process_images_batch

def load_data(path: str, extension: str) -> List[str] : 
  """ extension: '.jpg' or '.mp4' or '.jpeg' """
  if not os.path.isdir(path):
      print(f"AVISO: O diretório de entrada não foi encontrado: '{path}'. Pulando esta combinação de perfil/rede.")
      return []
      
  data = list(filter(
    lambda item: item.find(extension) >= 0,
    [ path+'/'+item for item in os.listdir(path)],
  ))
  
  return data

def extractID(file: str, exetension: str, path: str) -> str:
  file = file.replace(exetension, '')
  file = file.replace(path+'/', '')
  return file

def create_file_id(path_files, file_csv: str, perfil: str):
  
  files : List[str]= []
  files.extend(load_data(path_files, '.jpg'))

  data = []
  for file in files:
    data.append({'File': file, 'ID':extractID(file, '.jpg', path_files)})
      
  # Garante que o DataFrame sempre tenha as colunas 'ID' e 'File', mesmo que esteja vazio
  data = pd.DataFrame(data, columns=['ID', 'File'])
  
  if data.empty:
      print(f"AVISO: Nenhuma imagem encontrada em '{path_files}'. Criando arquivo de mapeamento vazio para este perfil/rede.")
      data.to_csv(file_csv, index=False) # Salva um DataFrame vazio com cabeçalhos
      return

  data["ID"] = data["ID"].apply(lambda x: x.replace(perfil, ""))
  data[["ID", "File"]].to_csv(file_csv, index=False)

# def send_to_google(data_entry: pd.DataFrame, path: str, vision: int) -> None:
#   """
#   Função antiga que enviava uma imagem de cada vez para a API.
#   Mantida aqui como referência.
#   """
#   for i in range(len(data_entry)):
#     """ 
#     new_data = pd.DataFrame([], columns=['ID', 'Class', 'Percent','Subclass',])
#     print('oi') 
#     """
#     if (vision == 1):
#       new_data = load_labels(path_image=data_entry.iloc[i]['File'], fileID=data_entry.iloc[i]['ID'])
#       if not os.path.isfile(path):
#         data = pd.DataFrame([], columns=['ID', 'Class', 'Percent','Subclass',])
#       else:
#         data = pd.read_csv(path)
#       data = pd.concat(([data, new_data]))
#       data.to_csv(path + ".csv", index=False)
#       data.to_excel(path + ".xlsx", index=False)


def save_vision_results(df: pd.DataFrame, path: str):
    """Salva os resultados da visão computacional em CSV e Excel."""
    output_path_csv = path
    if not output_path_csv.endswith('.csv'):
        output_path_csv += '.csv'
    
    output_path_xlsx = output_path_csv.replace('.csv', '.xlsx')

    if os.path.isfile(output_path_csv):
        existing_data = pd.read_csv(output_path_csv)
        df = pd.concat([existing_data, df], ignore_index=True)

    df.to_csv(output_path_csv, index=False)
    df.to_excel(output_path_xlsx, index=False)
      
def send_imagens_API(
  file_id: str,
  metadada: pd.DataFrame,
  vision: int =1,
  path_vision: str='Vision.csv',
  fake: bool = True
  ) -> None:
  """ 
    vision: 1 for google or 2 for amazon
    path: path file vision in csv
  """
  
  path_vision += '.csv'
  if vision == 1: 
    if not os.path.isfile(path_vision):
      data = pd.DataFrame([], columns=['ID', 'Class', 'Percent','Subclass',])
    else:
      data = pd.read_csv(path_vision)     
      data['ID'] = data['ID'].apply(str)
  elif vision == 2:
    if not os.path.isfile(path_vision):
      data = pd.DataFrame([], columns=['ID', 'Class', 'Percent','Subclass',])
    else:
      data = pd.read_csv(path_vision)
      data['ID'] = data['ID'].apply(str)
      
  data_file_id = pd.read_csv(file_id)
  data_file_id['ID'] == data_file_id['ID'].apply(str)
  data_file_id = data_file_id.loc[data_file_id['ID'].isin(metadada['ID'])]

  data_entry = data_file_id.loc[~data_file_id['ID'].isin(data['ID'])]
  
  k=100

  if not fake:
    for i in range(0, len(data_entry), k):
      # Lógica nova com processamento em lote
      batch = data_entry.iloc[i:i+k]
      print(f"Processando lote de {len(batch)} imagens... Restam {len(data_entry) - (i+len(batch))} imagens.")
      if vision == 1:
        results_df = process_images_batch(batch)
        if not results_df.empty:
          save_vision_results(results_df, path_vision)
      # A chamada para a função antiga seria aqui, dentro do loop:
      # send_to_google(data_entry[d-k: d], path=path_vision, vision=vision)
 
