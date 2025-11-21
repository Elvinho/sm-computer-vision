# CLUSTERING

Two major steps are proposed to proceed with the clustering:

1. Run the **automatic clustering**, based on the *overlap measure* between tags. 
   - It is a step of the script `social_media_visual_analysis-p1.py`. So, run this script first!
   - The output is saved in CSV and XLS files in `outputs/clustering`
   - A few different  (default: 3) clustering options are created and represented in columns named "Clustering Size [N]"

1. A **manual refinement of the clusters**, for which we proposed a specific methodology.
   - See the next section


## Manual Refinement of the Clusters

1. Open the output file for the desired dataset.
   - The name starts with `"5. Clustering-"` followed by the name of the dataset.
   - Open the file with extension `.xlsx` (not the `.csv` extension)

1. Analyze the different clustering options and choose the one that you find the best.
   - We recommend to choose the clustering that groups the tags in a meaningful way.
   - You may want to check the plot with the *silhouette scores* for each clustering size, in folder `outputs/clustering/clustering_scores_plots`

1. Adapt the clusters based on conceptual similarities between the tags, if you want. 
   - You may unify clusters whose tags are conceptually similar
   - Or you may divide clusters that mix tags conceptually different
   - In special, we *recomend* to divide/split clusters that mix tags with different statistical effects (of increasing/decreasing *likes*)

1. Save the refined clusterings.
   - Create a *new column* with a new name to identify your refined clustering, e.g. `Refined Clustering 1`
   - Use numbers or strings to uniquely identify the cluster for each tag
   - Save with the same name (and extension `.xlsx`) into the folder `outputs/clustering/refined`

1. To further analyze and improve the clustering, analyze images from the posts related to each cluster.
   To do this, first *download or retrieve the images*, naming each file with the ID of the post
   - For the dataset of the `2022 Brazilian Presidential Election`, the images are in a compressed file [in this link](https://drive.google.com/drive/folders/18_Nsuvz0oTroQQxT-CTYCJ3xlbgS1FLD)
   - Place the (extracted) images in the input folder, in subfolders named by the social network. Examples:
     * `input/facebook/<id_post>.jpg`
     * `input/tiktok/<id_post>.jpg`
     * `instagram/<id_post>.jpg`

1. Then, use the script `social_media_visual_analysis-p2.py` to select random images from the posts associated to each cluster.
   - First, *edit* the script to set the name of the column of the clustering, i.e. the column set in step `4`
   - Then, *run* the script, and it will read all the `.xls` files from folder `outputs/clustering/refined` and select random images for each cluster indicated in the given column
   - The selected images will be saved in directory `outputs/clustering/saved_images??????`

1. Analyze the images selected for each cluster to refine the clustering.
   - *Unify* clusters with images that depict similar scenes. 
   - It is not possible to split a cluster in this step.

1. Save the new clustering proposed (by unifying previous clusters):
   - Open the same file used in step `4`, and create a new column to be filled with the identification of the cluster
   - You may use numbers, letters or descriptive strings to identify the clusters
   - Give a new name to the column, e.g. `Refined Clustering 2`
   - We recommend to keep the previous clustering columns, as a documentation of the process
   

