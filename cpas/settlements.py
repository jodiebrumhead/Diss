from osgeo import gdal, ogr, osr
import rasterstats as rs
import geopandas as gpd
import pandas as pd
import numpy as np
import sys
from sklearn import cluster, neighbors, metrics
from scipy import spatial
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import tifs
from cs_test import find_coord
gdal.UseExceptions()


# https://gis.stackexchange.com/questions/321021/splitting-polygon-into-equal-area-polygons-in-qgis-3
# https://stackoverflow.com/questions/33440530/identify-unique-groupings-of-polygons-in-geopandas-shapely

# Input HRSL raster
raster = "/home/s1891967/diss/Data/Input/hrsl_settlement/hrsl_uga_pop.tif"

r = tifs.tiffHandle(raster)
r.readTiff(raster)

# r.data is the array from raster

"""

r.data = np.array([[0,0,1,0,0,0,0,0,0,1],
                    [0,0,0,0,0,0,1,1,2,0],
                    [1,0,0,0,0,0,0,1,1,0],
                    [0,0,0,0,1,0,0,1,0,0],
                    [0,1,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [1,0,0,0,0,0,0,0,0,0],
                    [0,1,3,1,0,0,1,0,0,1],
                    [1,1,1,0,0,0,0,0,0,0],
                    [0,0,0,0,0,1,0,0,0,0]])

"""

# Make -1 no data values 0
r.data = np.where(r.data < 0, 0, r.data)

# Identify index of pixels which are not zero i.e. have a population
pop_indices = np.transpose(np.nonzero(r.data))

# Create this into a usable format for later also? 
# TODO: check I actually needed this, maybe its just because I was doing other things wrong
meh_x, meh_y = np.nonzero(r.data)
pop_indices_formatted = [[i, j] for i,j in zip(meh_x,meh_y)]

# Create list of the values where data is non zero
pop_values = r.data[np.nonzero(r.data)]

# pop_values and pop_indices are then 2 1D lists in which the indexes link the values
# i.e. pop_indices[5] is where pop_values[5] is from

"""
# Nearest neighbour graphs for estimating DBSCAN epsilon
nbrs = neighbors.NearestNeighbors(n_neighbors=20, algorithm='auto', metric='euclidean').fit(pop_indices)
distances, indices = nbrs.kneighbors(pop_indices)
fourth_nnd = [distances[i][19] for i in range(len(distances))]
fourth_nnd.sort()
plt.plot(fourth_nnd)
plt.savefig('/home/s1891967/diss/Data/Output/eps.png')
"""

# DBSCAN parmeters
EPS_DISTANCE = 10
MIN_SAMPLE_POLYGONS = 15

# Undertake DBSCAN clustering
dbscan = cluster.DBSCAN(eps=EPS_DISTANCE, min_samples=MIN_SAMPLE_POLYGONS)
clusters = dbscan.fit(pop_indices)

# clusters.labels_ is then also a 1D list in which the indexes are the same as pop_indicies and pop_values

#print(metrics.silhouette_score(pop_indices, clusters.labels_))

tree_indices = []
df = pd.DataFrame(columns=['cluster', 'indices', 'cluster_pop'])

for clst in range(0, clusters.labels_.max() + 1): # range(0, max) rather than min max means the noise is ignored
    # for each cluster returned from the DBSCAN clustering
    c = np.where(clusters.labels_ == clst)
    # find the indexes in clusters.labels for that cluster
    # as the indexes are in the same order for clusters.labels_, pop_indices and pop_values
    # we can use these to find the cluster locations and values

    cluster_pop_totals = pop_values[c].sum() # find the sum of population in the cluster

    # TODO: add option to remove large clusters in here where > 5000 people as based upon Degree of Urbanization?
    # Will have to change some other bits further on to account for missing clusters... 

    clus_indices = pop_indices[c] # find the indices for the cluster
    tree_indices.append(clus_indices.tolist()) # use these to create list of points from which to build KDTree

    df = df.append({'cluster': clst,
                'indices': clus_indices,
                'cluster_pop': cluster_pop_totals},
                ignore_index=True)

# print number of clusters with pop greater than 5000

seriesObj = df.apply(lambda x: True if x['cluster_pop'] > 5000 else False , axis=1)
 
# Count number of True in series
print(len(seriesObj[seriesObj == True].index))

 


# Dealing with the noise.... 

# Flatten list of lists into single list of pixel coordinates
tree_indices = [val for sublist in tree_indices for val in sublist]
# Build KDTree
tree = spatial.KDTree(tree_indices)


# Account for population values that are in the noise
# Find indexes of noise
n = np.where(clusters.labels_ == -1)
n_ind = pop_indices[n]

nc = []

for i in n_ind:
    # i is the r.data location of the noise
    # for each noise pixel find the nearest clustered pixel
    idx = tree.query(i)[1]
    arr_location = tree_indices[idx] # this is the nearest cluster pixel to the noise pixel
    idx1 = pop_indices_formatted.index(arr_location)  # find the index of the cluster pixel in the list of pop_indices
    nc.append(clusters.labels_[idx1]) # use the index to find what cluster the noise pixel is nearest too

# nc then equals a list of the nearest cluster for each noise point

# TODO: use n_ind and nc to create tiff of the clusters and the associated noise points

noise_pop_total = []

for u in range(0, clusters.labels_.max() + 1):
    # for each cluster value in nc find a list of there indexes
    lst = [i for i, x in enumerate(nc) if x == u]
    noise_pop_total.append(pop_values[lst].sum()) # find the noise population for each cluster


df['noise_pop'] = noise_pop_total

df['total_pop'] = df['cluster_pop'] + df['noise_pop']

print(df)

centers = []


for index, row in df.iterrows():
    # Undertake k means clustering on regular points within polygon
    if row['total_pop']/4.9 > 100:
        kmeans = cluster.KMeans(n_clusters=int(row['total_pop']//100), random_state=0).fit(row['indices'])

        centers.append(kmeans.cluster_centers_.tolist())
    else:
        pass


#print(centers)

# Flatten to get list of points for all settlements
flatter = [val for sublist in centers for val in sublist]


y_ls, x_ls = map(list, zip(*flatter)) # unpack route list of tuples into 2 lists
xs, ys = find_coord(x_ls, y_ls,r) # convert pixel references to coords

gs1 = gpd.GeoSeries(gpd.points_from_xy(xs,ys))

#print(gs1)

gs1.to_file('/home/s1891967/diss/Data/Output/test_settlements.shp')





# kmeans parameter total cluster pop/ ??

# do k means on indexes

# return centres

# make these into points

# TODO: Something about the CRS
