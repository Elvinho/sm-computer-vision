# Bibliotecas
import pandas as pd
import researchpy as repr
from statistical_tests.statistical_tests import *
from qualitative_analysis.qualitative_analysis import *
import os

## Análise Descritiva e Estatística dos clusters escolhidos

input_1 = os.path.join('outputs', 'clustering', 'refined')
input_2 = os.path.join('outputs', 'normalize_posts')
common_column = 'Class'
cluster = 'Clustering_refined' # Certifique-se que este é o nome da sua coluna de cluster
target = 'Curtidas Normalizadas'
output_describe = os.path.join('outputs', 'qualitative_analysis', 'clusters')
output_sts = os.path.join('outputs', 'statistical_tests', 'clusters')
output_2_sts = os.path.join('outputs', 'statistical_tests', 'cluster_vs_cluster')

describe_cluster_folder(input_1, input_2, common_column, cluster, target, output_describe)
stats_cluster_folder(input_1, input_2, common_column, cluster, target, output_sts, output_2_sts)
