import pandas as pd
from google.cloud import vision
import io
import os
from typing import List
from typing import Sequence # Adicionado para o código antigo

GOOGLE_APPLICATION_CREDENTIALS='./caminho que aponta para json gerado na aplicacao do goole'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS

def process_images_batch(image_df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa um lote de imagens usando a API Google Vision e retorna um DataFrame com os resultados.

    Args:
        image_df (pd.DataFrame): DataFrame contendo as colunas 'File' (caminho da imagem) e 'ID'.

    Returns:
        pd.DataFrame: DataFrame com as colunas ['ID', 'Class', 'Percent', 'Subclass'].
    """
    # --- INÍCIO DO NOVO CÓDIGO (PROCESSAMENTO EM LOTE) ---
    client = vision.ImageAnnotatorClient()
    features = [
        {"type_": vision.Feature.Type.LABEL_DETECTION},
        {"type_": vision.Feature.Type.OBJECT_LOCALIZATION},
        {"type_": vision.Feature.Type.FACE_DETECTION},
        {"type_": vision.Feature.Type.TEXT_DETECTION},
    ]

    requests = []
    for index, row in image_df.iterrows():
        path = row['File']
        try:
            with io.open(path, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            request = vision.AnnotateImageRequest(image=image, features=features)
            requests.append(request)
        except FileNotFoundError:
            print(f"Arquivo não encontrado, pulando: {path}")
            continue
        except Exception as e:
            print(f"Erro ao ler o arquivo {path}: {e}")
            continue
    
    if not requests:
        return pd.DataFrame()

    batch_response = client.batch_annotate_images(requests={"requests": requests})

    all_results = []
    for i, response in enumerate(batch_response.responses):
        if response.error.message:
            print(f'Erro para a imagem {image_df.iloc[i]["File"]}: {response.error.message}')
            continue

        file_id = image_df.iloc[i]['ID']

        for label in response.label_annotations:
            all_results.append({'ID': file_id, 'Class': label.description, 'Percent': label.score, 'Subclass': 'label'})
        for obj in response.localized_object_annotations:
            all_results.append({'ID': file_id, 'Class': obj.name, 'Percent': obj.score, 'Subclass': 'object'})
        for face in response.face_annotations:
            face_details = {
                "Joy": face.joy_likelihood, "Sorrow": face.sorrow_likelihood,
                "Anger": face.anger_likelihood, "Surprise": face.surprise_likelihood,
                "UnderExposed": face.under_exposed_likelihood, "Blurred": face.blurred_likelihood,
                "Headwear": face.headwear_likelihood
            }
            for detail, likelihood in face_details.items():
                # Adiciona a tag apenas se a probabilidade for POSSÍVEL ou maior
                if likelihood >= vision.Likelihood.POSSIBLE:
                     all_results.append({'ID': file_id, 'Class': detail, 'Percent': face.detection_confidence, 'Subclass': 'face'})

        if response.text_annotations:
            all_results.append({'ID': file_id, 'Class': response.text_annotations[0].description.replace('\n', ' '), 'Percent': 1.0, 'Subclass': 'text'})

    return pd.DataFrame(all_results, columns=['ID', 'Class', 'Percent', 'Subclass'])
    # --- FIM DO NOVO CÓDIGO ---


"""
--- INÍCIO DO CÓDIGO ANTIGO (PROCESSAMENTO INDIVIDUAL) ---
Mantido aqui como referência.
"""

def analyze_image_from_uri(
  image_uri: str,
  feature_types: Sequence,
) -> vision.AnnotateImageResponse:
  client = vision.ImageAnnotatorClient()
  with open(image_uri, "rb") as image_file:
    content = image_file.read()
  image = vision.Image(content=content)
  features = [vision.Feature(type_=feature_type) for feature_type in feature_types]
  request = vision.AnnotateImageRequest(image=image, features=features)
  response = client.annotate_image(request=request)
  return response

def create_row(lista: List, fileID: str, classe: str, subclass: str, percent: float) -> None:
  el = {
    'ID': fileID,
    'Class': classe,
    'Percent': round(percent, 2),
    'Subclass': subclass
  }
  if (el not in lista):
    lista.append(el)

def rows_data(response: vision.AnnotateImageResponse, fileID:str) -> List:
  rows = []
  # OBJECT
  for obj in response.localized_object_annotations:
    create_row(lista=rows, fileID=fileID, classe=obj.name, percent=obj.score, subclass='object')
  # LABELS
  for label in response.label_annotations:
    create_row(lista=rows, fileID=fileID, classe=label.description, percent=label.score, subclass='label')
  # FACE
  for face in response.face_annotations:
    face_details = {
      "Joy": face.joy_likelihood, "Sorrow": face.sorrow_likelihood,
      "Anger": face.anger_likelihood, "Surprise": face.surprise_likelihood,
      "UnderExposed": face.under_exposed_likelihood, "Blurred": face.blurred_likelihood,
      "Headwear": face.headwear_likelihood
    }
    for key, likelihood in face_details.items():
      if likelihood >= vision.Likelihood.POSSIBLE:
        create_row(lista=rows, fileID=fileID, classe=key, percent=face.detection_confidence, subclass='face')
  # TEXT
  if response.text_annotations:
    try:
      create_row(
        lista=rows, fileID=fileID, classe=response.text_annotations[0].description.replace('\n', ' '),
        percent=1, subclass='text'
      )
    except IndexError:
      pass # No text found
  return rows

def load_labels(path_image: str, fileID: str = None) -> pd.DataFrame:
  if fileID is None:
      fileID = path_image
  features = [
    vision.Feature.Type.OBJECT_LOCALIZATION,
    vision.Feature.Type.FACE_DETECTION,
    vision.Feature.Type.LABEL_DETECTION,
    vision.Feature.Type.TEXT_DETECTION,
  ]
  response = analyze_image_from_uri(path_image, features)
  return pd.DataFrame(rows_data(response, fileID))
"""
--- FIM DO CÓDIGO ANTIGO ---
"""