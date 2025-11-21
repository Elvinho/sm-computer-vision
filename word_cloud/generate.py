import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

def count_labels(df:pd.DataFrame, output: str):
  df_count = df.groupby(['Class']).size().reset_index(name="Total")
  df_count.sort_values("Total", ascending=False)
  df_count.to_excel(f"{output}.xlsx", index=False)
  
def create_wordcloud(df: pd.DataFrame, path: str, output: str):
  output = f"{output}/wordcloud"
  if (not os.path.isdir(output)):
    os.mkdir(output)
    
  count_labels(
    df,
    output=f"{output}/{path}"
  )
  
  classes = df.groupby('Class').size().reset_index(name="Total")
  classes['Class'] = classes['Class'].str.replace(' ', '_')
  key_value = {}
  for key, total in classes.values:
    key_value[key] = total
  
  wordcloud = WordCloud(
    background_color='white',
    width=2000,
    height=1000,
    max_words=200,
    relative_scaling=0
    )
  wordcloud.generate_from_frequencies(key_value)
  plt.figure(figsize=(100, 70))
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis('off')
  plt.savefig(f"{output}/{path}.jpg")
  plt.close()
  
