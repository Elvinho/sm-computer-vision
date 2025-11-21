# AGRUPAMENTO
Duas etapas principais são propostas para realizar o agrupamento:

Executar o agrupamento automático, baseado na medida de sobreposição entre as tags.

Esta etapa faz parte do script social_media_visual_analysis-p1.py. Portanto, execute este script primeiro!

O resultado é salvo em arquivos CSV e XLS na pasta outputs/clustering.
Algumas opções de agrupamento diferentes (padrão: 3) são criadas e representadas em colunas chamadas "Tamanho do Agrupamento [N]".
Um refinamento manual dos agrupamentos, para o qual propusemos uma metodologia específica.

Consulte a próxima seção:

# Refinamento Manual dos Agrupamentos.

Abra o arquivo de saída para o conjunto de dados desejado.

O nome começa com "5. Clustering-" seguido pelo nome do conjunto de dados.

Abra o arquivo com a extensão .xlsx (não a extensão .csv).
Analise as diferentes opções de agrupamento e escolha a que você considerar melhor.

Recomendamos escolher o agrupamento que agrupe as tags de forma significativa.
Você pode verificar o gráfico com as pontuações de silhueta para cada tamanho de agrupamento, na pasta outputs/clustering/clustering_scores_plots.
Adapte os agrupamentos com base em semelhanças conceituais entre as tags, se desejar.

Você pode unificar agrupamentos cujas tags sejam conceitualmente semelhantes.
Ou pode dividir agrupamentos que misturem tags conceitualmente diferentes.
Em especial, recomendamos dividir/separar agrupamentos que misturem tags com diferentes efeitos estatísticos (de aumento/diminuição de curtidas).
Salve os agrupamentos refinados.

Crie uma nova coluna com um novo nome para identificar seu agrupamento refinado, por exemplo, Agrupamento Refinado 1.
Use números ou strings para identificar exclusivamente o agrupamento para cada tag.
Salve com o mesmo nome (e extensão .xlsx) na pasta outputs/clustering/refined.
Para analisar e aprimorar ainda mais o agrupamento, analise as imagens das postagens relacionadas a cada agrupamento. Para isso, primeiro baixe ou extraia as imagens, nomeando cada arquivo com o ID da publicação.

Para o conjunto de dados da Eleição Presidencial Brasileira de 2022, as imagens estão em um arquivo compactado neste link.
Coloque as imagens (extraídas) na pasta `input`, em subpastas nomeadas de acordo com a rede social. Exemplos:
`input/facebook/<id_post>.jpg`
`input/tiktok/<id_post>.jpg`
`instagram/<id_post>.jpg`
Em seguida, use o script `social_media_visual_analysis-p2.py` para selecionar imagens aleatórias das publicações associadas a cada cluster.

Primeiro, edite o script para definir o nome da coluna de clusterização, ou seja, a coluna definida na etapa 4.
Em seguida, execute o script, que lerá todos os arquivos .xls da pasta `outputs/clustering/refined` e selecionará imagens aleatórias para cada cluster indicado na coluna especificada.
As imagens selecionadas serão salvas no diretório `outputs/clustering/saved_images`. Analise as imagens selecionadas para cada cluster para refinar o agrupamento.

Unifique os clusters com imagens que retratam cenas semelhantes.

Não é possível dividir um cluster nesta etapa.

Salve o novo agrupamento proposto (unificando os clusters anteriores):

Abra o mesmo arquivo usado na etapa 4 e crie uma nova coluna para ser preenchida com a identificação do cluster.
Você pode usar números, letras ou strings descritivas para identificar os clusters.
Dê um novo nome à coluna, por exemplo, Agrupamento Refinado 2.
Recomendamos manter as colunas de agrupamento anteriores como documentação do processo.