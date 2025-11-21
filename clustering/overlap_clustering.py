import os

# Set this environment variable to avoid a specific warning when running K-Means
os.environ["OMP_NUM_THREADS"] = "1"

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from tqdm import tqdm


# Seed used by the K-Means algorithm
RAND_STATE = 11


# The constants below are for experimental features or for debugging
OVERLAP_METRIC         = 1      # Tag overlap metric to be used. Options: 1 (default) or 2 (alternative)
WEIGHTED_CLUSTERS      = False  # If True, clusterings will be calculated using weights proportional to the number of posts associated to each tag
GENERATE_INERTIA_PLOTS = False  # If True, generates the plots for inertia scores (beyond the plots for silhoutte scores)



def clusterize_tags(file_tags_stats, 
                    file_tags_per_post, 
                    output_dir, 
                    out_file_base_name,
                    cluster_size_range=range(3, 10+1),
                    top_n_clusterings=3):
    '''
    Parameters:
    - file_tags_stats:    CSV or XLS file with the results of the statistical tests per tag
    - tags_per_post_file: CSV or XLS file with the tags associated with each post
    - output_dir:         directory where the output files will be saved
    - out_file_base_name: base name for files written by this function
    - cluster_size_range: range of cluster sizes to be explored
    - top_n_clusterings:  indicates the number of the best clusters (by silhouette score) to be reported in the output file
    '''
    file_tags_stats = os.path.abspath(file_tags_stats)
    print(f"####### File '{file_tags_stats}' #######\n")

    # (1) LOADS THE DATA
    if file_tags_per_post.endswith('.xlsx'):
        df_posts_tags = pd.read_excel(file_tags_per_post)
    else:
        df_posts_tags = pd.read_csv(file_tags_per_post)

    if file_tags_stats.endswith('.xlsx'):
        df_all_tags_stats = pd.read_excel(file_tags_stats)
    else:
        df_all_tags_stats = pd.read_csv(file_tags_stats)

    # creates the directory for plot images and defines the template for their file names
    plot_output_dir = f'{output_dir}/clustering_scores_plots'
    os.makedirs(plot_output_dir, exist_ok=True)
    out_file_base_name = out_file_base_name[0:out_file_base_name.rfind(".")] # remove extension
    
    plot_filepath_template = f"{plot_output_dir}/##PLOTNAME##-{out_file_base_name}-##CLUSTERING##.png"

    # (2) SOME PRE-PROCESSING
    df_posts_tags = df_posts_tags[['ID', 'Class']].drop_duplicates()
    assert df_posts_tags.isna().sum().sum() == 0, 'There are NaNs in the dataframe!'

    df_output_tags_stats = df_all_tags_stats[df_all_tags_stats['Classification'].isin(['greater', 'less'])].reset_index(drop=True)
    df_output_tags_stats = df_output_tags_stats[['Class', 'Classification']].copy()
    df_output_tags_stats.loc[:, 'Increases Likes'] = (df_output_tags_stats['Classification'] == 'greater')
    df_output_tags_stats.loc[:, 'Decreases Likes'] = (df_output_tags_stats['Classification'] == 'less')
    df_output_tags_stats.drop(columns=['Classification'], inplace=True)

    assert (~df_output_tags_stats['Increases Likes'] & ~df_output_tags_stats['Decreases Likes']).sum() == 0, 'There are tags that neither increase nor decrease likes'
    assert df_output_tags_stats['Class'].duplicated().sum() == 0, 'There are duplicated tags in the dataframe'
    df_output_tags_stats.drop(columns=['Decreases Likes'], inplace=True)

    # data series only with the selected tags
    selected_tags = df_output_tags_stats['Class']

    # adiciona a quantidade de postagens
    ds_tag_posts_count = df_posts_tags.loc[df_posts_tags['Class'].isin(selected_tags)].groupby('Class')['ID'].nunique()
    ds_tag_posts_count.name = 'Posts Count'
    df_output_tags_stats = df_output_tags_stats.merge(ds_tag_posts_count, on='Class', how='left')

    # (3) CRIA A MATRIZ DE OVERLAPPING
    print(f"- Calculating overlappings with metric {OVERLAP_METRIC}...")
    if OVERLAP_METRIC == 1:
        df_tag_overlapping = create_overlapping_matrix(df_posts_tags, selected_tags, overlap_metric1)
    else:
        # adapts the function overlap_metric2 to be used with create_overlapping_matrix
        def overlap_metric2_simplified(tagA, tagB, df):
            return overlap_metric2(tagA, tagB, df, df_output_tags_stats)
        df_tag_overlapping = create_overlapping_matrix(df_posts_tags, selected_tags, overlap_metric2_simplified)
    
    df_tag_overlapping = df_tag_overlapping.reset_index(drop=True)
    print()

    # (4) CRIA AS CLUSTERIZACOES
    if WEIGHTED_CLUSTERS:
        print("- Calculating weights for the clusters...\n")
        # pesso definidos a partir da quantidade de postagens
        df_weights = 100.0 * ds_tag_posts_count / ds_tag_posts_count.sum()
    else:
        df_weights = None
    
    df_tags_to_clusters, best_sizes = kmeans_clusterize(df_tag_overlapping, "Clustering Size ", 
                                                         cluster_size_range, top_n_clusterings,
                                                         plot_filepath_template, weights=df_weights)
    df_output_tags_stats = df_output_tags_stats.merge(df_tags_to_clusters, on='Class')
    
    # (5) CONTA AS QUANTIDADES DE POSTS DE CADA CLUSTER
    for size in best_sizes:
        clustering_label = "Clustering Size " + str(size)
        df_cluster_to_postcount = count_posts_per_cluster(df_output_tags_stats, df_posts_tags, clustering_label)
        df_output_tags_stats = df_output_tags_stats.merge(df_cluster_to_postcount, on=clustering_label)

    # (6) ALINHA OS LABELS DOS CLUSTERS (PARA FACILITAR COMPARAÇÃO)
    best_sizes = sorted(best_sizes)
    columns_to_sort_by = [ f"Clustering Size {best_sizes[0]}" ]
    
    for i in range(1, len(best_sizes)):
        df_output_tags_stats = align_clusterings(df_output_tags_stats, 
                                                   f"Clustering Size {best_sizes[i-1]}", f"Clustering Size {best_sizes[i]}")
        columns_to_sort_by.append(f"Clustering Size {best_sizes[i]}") 
    
    columns_to_sort_by.append('Increases Likes')
    df_output_tags_stats = df_output_tags_stats.sort_values(by=columns_to_sort_by).reset_index(drop=True)
    
    # (7) SALVA ARQUIVOS DE SAÍDA
    if OVERLAP_METRIC == 1 and WEIGHTED_CLUSTERS == False:
        out_file = f'5. Clusterings-{out_file_base_name}.csv'
    elif WEIGHTED_CLUSTERS:
        out_file = f'5. Clusterings-{out_file_base_name}-metric{OVERLAP_METRIC}-weighted.csv'
    else:
        out_file = f'5. Clusterings-{out_file_base_name}-metric{OVERLAP_METRIC}-unweighted.csv'
    
    df_output_tags_stats.to_csv(f'{output_dir}/{out_file}', index=False)
    
    out_file = out_file.replace('.csv', '.xlsx')
    df_output_tags_stats.to_excel(f'{output_dir}/{out_file}', index=False)


def overlap_metric1(tagA, tagB, df):
    setA = df[df['Class'] == tagA]['ID'].unique()
    setB = df[df['Class'] == tagB]['ID'].unique()
    set_inter_A_B = np.intersect1d(setA, setB)
    overlap_A_B = len(set_inter_A_B) / len(setB)
    overlap_B_A = len(set_inter_A_B) / len(setA)
    return overlap_A_B, overlap_B_A


# This is an alternative metric to measure tag overlap. 
def overlap_metric2(tagA, tagB, df, df_statistical_test):
    tagA_increases_likes = df_statistical_test.loc[df_statistical_test['Class'] == tagA, 'Increases Likes'].values[0]
    ids_with_tagA = df[df['Class'] == tagA]['ID'].unique()
    if tagA_increases_likes:
        setA = ids_with_tagA
    else:
        # remember that an ID may be associated with more than one tag/class
        ids_without_tagA = df[ ~df['ID'].isin(ids_with_tagA) ]
        # alt.: ids_without_tagA = np.setdiff1d(df['ID'].unique(), ids_with_tagA)
        ids_without_tagA = ids_without_tagA['ID'].unique()
        setA = ids_without_tagA

    tagB_increases_likes = df_statistical_test.loc[df_statistical_test['Class'] == tagB, 'Increases Likes'].values[0]
    ids_with_tagB = df[df['Class'] == tagB]['ID'].unique()
    if tagB_increases_likes:
        setB = ids_with_tagB
    else:
        # remember that an ID may be associated with more than one tag/class
        ids_without_tagB = df[ ~df['ID'].isin(ids_with_tagB) ]
        ids_without_tagB = ids_without_tagB['ID'].unique()
        setB = ids_without_tagB

    set_intersection = np.intersect1d(setA, setB)
    overlap_A_B = len(set_intersection) / len(setB)
    overlap_B_A = len(set_intersection) / len(setA)
    
    return overlap_A_B, overlap_B_A


def create_overlapping_matrix(df_posts_tags, selected_tags, overlap_fn):
    df_tag_overlapping = pd.DataFrame(columns=selected_tags, index=selected_tags)

    for i in tqdm(range(len(selected_tags))):
        tag1 = selected_tags[i]
        #print(tag1)
        for j in range(i, len(selected_tags)):
            tag2 = selected_tags[j]
            overlap_tag1_tag2, overlap_tag2_tag1 = overlap_fn(tag1, tag2, df_posts_tags)
            df_tag_overlapping.loc[tag1,tag2] = overlap_tag1_tag2
            df_tag_overlapping.loc[tag2,tag1] = overlap_tag2_tag1

    return df_tag_overlapping


def align_clusterings(df_selected_tags_stats, clustering1_col, clustering2_col):
    """
    This function aligns the labels of 'clustering2' with those of 'clustering1'. 
    It does so by replacing each label in 'clustering2' with the label of the cluster in 'clustering1' 
    that has the maximum intersection. This is done without repeating a label from 'clustering1'. 
    Note that 'clustering1' remains unmodified during this process.
    """
    def cluster_to_letter(cluster):
        return chr(cluster + 65)
    df_selected_tags_stats[clustering2_col] = df_selected_tags_stats[clustering2_col].apply(cluster_to_letter)

    available_cluster1_ids = df_selected_tags_stats[clustering1_col].sort_values().unique().tolist()
    next_unused_cluster_id = df_selected_tags_stats[clustering1_col].max() + 1

    # analisa clusters do clustering2 por ordem decrescente de quantidade de tags
    for c2 in df_selected_tags_stats[clustering2_col].value_counts().index: 
        set_cluster_2 = df_selected_tags_stats[df_selected_tags_stats[clustering2_col] == c2]['Class']
        max_intersection = 0
        max_intersection_cluster_1 = -1
        for c1 in available_cluster1_ids:
            set_cluster_1 = df_selected_tags_stats[df_selected_tags_stats[clustering1_col] == c1]['Class']
            set_intersection = np.intersect1d(set_cluster_1, set_cluster_2)
            if len(set_intersection) > max_intersection:
                max_intersection = len(set_intersection)
                max_intersection_cluster_1 = c1
        if max_intersection > 0:
            df_selected_tags_stats.loc[:, clustering2_col].replace(c2, max_intersection_cluster_1, inplace=True)
            # remove o cluster 1 da lista de clusters disponíveis
            available_cluster1_ids.remove(max_intersection_cluster_1)
        else:
            df_selected_tags_stats.loc[:, clustering2_col].replace(c2, next_unused_cluster_id, inplace=True)
            next_unused_cluster_id += 1

    return df_selected_tags_stats


def kmeans_clusterize(df_tag_overlapping, clustering_label_prefix, cluster_size_range, top_n_clusters, plot_filepath_template, weights=None):
    inertia_values = []
    silhouette_scores = []

    if weights is not None:
        df_tag_overlapping = df_tag_overlapping.mul(weights, axis=1)

    # to avoid the case where the number of clusters is greater than the number of tags
    cluster_max_size = min(max(cluster_size_range), len(df_tag_overlapping)-1)
    cluster_size_range = range(2, cluster_max_size+1)

    print(f"- Exploring clustering sizes in {cluster_size_range}")
    for size in tqdm(cluster_size_range):
        kmeans = KMeans(n_clusters=size, n_init=20, random_state=RAND_STATE).fit(df_tag_overlapping)
        inertia_values.append(kmeans.inertia_)
        labels = kmeans.labels_
        silhouette_avg = silhouette_score(df_tag_overlapping, labels)
        silhouette_scores.append(silhouette_avg)
        #print(f"  - cluster size: {size}, inertia: {kmeans.inertia_}, silhouette: {silhouette_avg}")
    print()

    if GENERATE_INERTIA_PLOTS:
        # plot the graph of cluster size vs. intertia
        plt.figure()
        plt.title('KMeans - Number fo clusters x Inertia')
        plt.plot(cluster_size_range, inertia_values, '-o')
        plt.xlabel('Cluster Size')
        plt.ylabel('Inertia')
        plt.xticks(range(min(cluster_size_range), max(cluster_size_range)+1, 2))
        out_filepath = plot_filepath_template.replace("##CLUSTERING##", f"m{OVERLAP_METRIC}{'w' if WEIGHTED_CLUSTERS else ''}") \
                                                 .replace("##PLOTNAME##", "InertiaValues")
        plt.savefig(out_filepath)

    # plot the graph of cluster size vs. silhouette scores (bestter than intertia for choosing the number of clusters)
    plt.figure()
    plt.title(f'Number of Clusters x Silhouette Score')
    plt.plot(cluster_size_range, silhouette_scores, '-x', label='Silhouette')
    plt.xlabel('Cluster Size')
    plt.ylabel('Silhouette')
    plt.xticks(range(min(cluster_size_range), max(cluster_size_range)+1, 2))
    out_filepath = plot_filepath_template.replace("##CLUSTERING##", f"m{OVERLAP_METRIC}{'w' if WEIGHTED_CLUSTERS else ''}") \
                                            .replace("##PLOTNAME##", "SilhouetteScore")
    plt.savefig(out_filepath)

    # creates clusterings with the best cluster sizes (by silhouette score)
    best_indexes = np.argsort(silhouette_scores)[::-1][:top_n_clusters]
    best_cluster_sizes = np.array(cluster_size_range)[best_indexes]
    print("- Best cluster sizes are", best_cluster_sizes, "\n")

    df_tags_to_clusters = pd.DataFrame(columns=['Class'])
    df_tags_to_clusters['Class'] = df_tag_overlapping.columns    # a ordem das colunas é a mesma ordem das linhas de df_tag_overlapping
    
    for cluster_size in best_cluster_sizes:
        clustering_label = clustering_label_prefix + str(cluster_size)
        print(f"- Creating '{clustering_label}' with {cluster_size} clusters\n")
        REPETITIONS = 100
        best_model = KMeans(n_clusters=cluster_size, n_init=REPETITIONS).fit(df_tag_overlapping)
        df_tags_to_clusters[clustering_label] = best_model.labels_   # labels dos clusters, ordenados pelas linhas do df_tag_overlapping

    return df_tags_to_clusters, best_cluster_sizes


def count_posts_per_cluster(df_selected_tags_stats, df_posts_tags, clustering):
    # 'ID' identifies the post, and 'Class' identifies the tag
    df_cluster_to_posts = df_posts_tags[['ID', 'Class']].merge(df_selected_tags_stats[['Class', clustering]], on='Class')
    assert df_cluster_to_posts.duplicated().sum() == 0, 'There are duplicated posts in the dataframe'
    
    df_cluster_to_posts = df_cluster_to_posts.groupby(clustering)['ID'].nunique().reset_index()
    df_cluster_to_posts.rename(columns={'ID': f'{clustering} Posts Count'}, inplace=True)
    return df_cluster_to_posts



# For testing purposes
if __name__ == "__main__":
    outputPath = "outputs"
    path_results_statistical = f'{outputPath}/statistical_tests/classes'

    # Cria várias opções de clusterizações das tags com diferentes quantidades de "grupos"
    # São escolhidas as "top_n_clusterings" quantidades de maior sillhouette score
    # Também são geradas arquivos dos gráficos dos sillhouette scores para cada quantidade de grupos considerada
    paths_statisticals = os.listdir(path_results_statistical)
    paths_statisticals = [ path.replace("4. Statistical_Test-", "") for path in filter(lambda path: path.find(".csv") >= 0, paths_statisticals)]

    for file in paths_statisticals:
        clusterize_tags(f"{outputPath}/statistical_tests/classes/4. Statistical_Test-{file}", 
                        f"{outputPath}/normalize_posts/2. Normalized-{file}",
                        f"{outputPath}/clustering/", 
                        file,
                        top_n_clusterings=3)
