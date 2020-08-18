"""
settlements.py: A python script to analyse HRSL data to identify potential rural DHS clusters.

N.B. uses input shapefile to batch process - suggested admin boundaries are used. 
N.B. uses landcover to determine where could be populated
"""

# Imports
from osgeo import gdal, ogr, osr, gdalconst
import geopandas as gpd
import pandas as pd
import numpy as np
import sys
from sklearn import cluster, neighbors, metrics
import time
from scipy import spatial
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

import tifs
import ru_class
from cs_test import find_coord

# Shpw gdal warnings
gdal.UseExceptions()

# start timer
start = time.time()

# Inputs
# Landcover -  used to determine what is unpopulated land rather than water or not Uganda
lc_filepath = '/home/s1891967/diss/Data/Input/UgandaLandCover/Uganda_Sentinel2_LULC2016.tif'

# HRSL - High Resolution Satellite Layer (any gridded pop dataset would work but parameters would need to be changed)
hrsl_filepath = "/home/s1891967/diss/Data/Input/Population/hrsl_Uganda.tif"

# District boundary shapefile
districts_fn = "/home/s1891967/diss/Data/Input/dist_reproj.shp"


# Processes

# Load HRSL data
hrsl = tifs.tiffHandle(hrsl_filepath)
hrsl.readTiff(hrsl_filepath)

# Create empty array of same dimensions as HRSL
hrsl.emptyTiff()

# Resample Landcover to 30m (HRSL) resolution
inp = gdal.Open(lc_filepath, gdalconst.GA_ReadOnly)
inputProj = inp.GetProjection()
inputTrans = inp.GetGeoTransform()

gdal.ReprojectImage(inp, hrsl.dst_ds, inputProj, hrsl.proj, gdalconst.GRA_NearestNeighbour)
lc_resampled = hrsl.dst_ds.GetRasterBand(1).ReadAsArray()


# Where water make null value
hrsl.data = np.where(lc_resampled == 10, np.NaN, hrsl.data)

# where not in Uganda make null value
hrsl.data = np.where(lc_resampled == lc_resampled, hrsl.data, np.NaN)

lc_resampled = None # tidy up no longer needed

# where no population but land make 0 
hrsl.data = np.where(hrsl.data < 0, 0, hrsl.data)

# round to 2 decimal places
hrsl.data = np.round(hrsl.data, 2)


# Load districts shapefile
source_ds = ogr.Open(districts_fn)
source_layer = source_ds.GetLayer()
feature = source_layer.GetNextFeature()
# Create a list of districts
districts = set([feature.GetFieldAsString('District') for feature in source_layer])

centers = [] # empty list to add to later
cnt = 0 # simple counter

# Batch process one district at a time
for d in districts:

    cnt = cnt + 1  # simple counter and print statement below to indicate
    print(f'Processing {d} no. {cnt} out of 128') 

    # create SQL string to select one district at a time
    sql_str = f"SELECT * FROM dist_reproj WHERE District='{d}'" 

    # rasterize one district at a time
    # to in-memory array sized based on landcover input
    hrsl.emptyTiff() # new empty tiff for rasterizing...

    opt = gdal.RasterizeOptions(burnValues=1, # value to assign to pixel 
                                allTouched=True, # value assigned to all pixels touched by line
                                SQLStatement=sql_str, # use above SQL string
                                SQLDialect='SQLITE')
    gdal.Rasterize(hrsl.dst_ds, districts_fn, options=opt) #(in-memory array, districts shapefile, above options)

    # Read from new in-memory tiff into array
    district_raster = hrsl.dst_ds.GetRasterBand(1).ReadAsArray()

    # then use rasterized district array to select relevant part of hrsl data
    district_hrsl = np.where(district_raster == 1, hrsl.data, np.NaN)

    # make all NaN's to be 0 so they are not identified
    district_hrsl = np.where(district_hrsl != district_hrsl, 0, district_hrsl)


    # Get data ready for clustering

    # Identify index of pixels which are not zero i.e. have a population
    pop_indices = np.transpose(np.nonzero(district_hrsl))

    print(len(pop_indices)) # useful check to see how many points you are trying to cluster
    
    # Create this into a usable format for later also
    meh_x, meh_y = np.nonzero(district_hrsl)
    pop_indices_formatted = [[i, j] for i,j in zip(meh_x,meh_y)]
    
    # Create list of the popoulation values where data is non zero
    pop_values = district_hrsl[np.nonzero(district_hrsl)] # prob could change this to pop_indices
        
    # pop_values and pop_indices are then 2 1D lists in which the indexes link the values
    # i.e. pop_indices[5] is where pop_values[5] is from


    # DBSCAN parmeters
    EPS_DISTANCE = 8.3
    MIN_SAMPLE_POLYGONS = 15

    print('Clustering...')
    # Undertake DBSCAN clustering on populated grid cell indices
    dbscan = cluster.DBSCAN(eps=EPS_DISTANCE, min_samples=MIN_SAMPLE_POLYGONS)
    clusters = dbscan.fit(pop_indices)
    #print(np.unique(clusters.labels_))
    print('Done clustering!')

    # clusters.labels_ is then also a 1D list in which the indexes are the same as pop_indicies and pop_values
    #print(metrics.silhouette_score(pop_indices, clusters.labels_))

    # Empties to fill
    tree_indices = []
    df = pd.DataFrame(columns=['cluster', 'indices', 'cluster_pop'])

    # for each cluster returned from the DBSCAN clustering
    for clst in range(0, clusters.labels_.max() + 1): # range(0, max) rather than min max means the noise is ignored

        c = np.where(clusters.labels_ == clst)
        # find the indexes in clusters.labels for that cluster
        # as the indexes are in the same order for clusters.labels_, pop_indices and pop_values
        # we can use these to find the cluster locations and values

        cluster_pop_totals = pop_values[c].sum() # find the sum of population in the cluster
        #print(f'Cluster {clst} in district {d} has a population of {cluster_pop_totals}')

        clus_indices = pop_indices[c] # find the indices for the cluster

        # Test if cluster is rural or urban
        # hrsl.data rather than distrct_hrsl input as this has the water and outside Uganda as NaN
        # and non populated land 0
        if ru_class.rural_test(hrsl.data, clus_indices, cluster_pop_totals):
            # only do this if not rural test = true

            # indices to use to build KD tree
            tree_indices.append(clus_indices.tolist()) # use these to create list of points from which to build KDTree

            # append details to dataframe
            df = df.append({'cluster': clst,
                        'indices': clus_indices,
                        'cluster_pop': cluster_pop_totals},
                        ignore_index=True)


    print('Dealing with the noise') 
    # Dealing with the noise.... 

    # Flatten list of lists into single list of pixel coordinates
    tree_indices = [val for sublist in tree_indices for val in sublist]

    if len(tree_indices) > 0: # this is needed as Kampala has no noise and no rural clusters

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

        noise_pop_total = []

        for u in range(0, len(df.index)): 
            # for each cluster value in nc find a list of there indexes
            lst = [i for i, x in enumerate(nc) if x == u]
            noise_pop_total.append(pop_values[lst].sum()) # find the noise population for each cluster

    else:
        noise_pop_total = 0

    # Add new totals to dataframe
    df['noise_pop'] = noise_pop_total
    df['total_pop'] = df['cluster_pop'] + df['noise_pop']

    print(df)

    # for each cluster in the dataframe
    for index, row in df.iterrows():
        # Undertake k means clustering on regular points within polygon
        if row['total_pop'] > 1470: #Large EAs i.e. more than 300 households were split up 300*4.9 = 1470
            NumberCluster = int(row['total_pop']//1470)
            ToCluster = row['indices']

            # some exceptional clusters have very high noise population and therefore more clusters than indices to cluster
            if NumberCluster > len(ToCluster):
                NumberCluster = len(ToCluster)

            kmeans = cluster.KMeans(n_clusters=NumberCluster, random_state=0).fit(ToCluster)
            # use centre of kmeans cluster as point
            centers.append(kmeans.cluster_centers_.tolist())
        else:
            # find centre of cluster indices
            a = np.sum(row['indices'][0:,0])/np.size(row['indices'][0:,0])
            b = np.sum(row['indices'][0:,1])/np.size(row['indices'][0:,1])
            centers.append([[a,b]])
#print(centers)

# Flatten to get single list of points for all potential rural DHS clusters
flatter = [val for sublist in centers for val in sublist]
#print(flatter)

y_ls, x_ls = map(list, zip(*flatter)) # unpack tuples into 2 lists
xs, ys = find_coord(x_ls, y_ls, hrsl) # convert pixel references to coords

# Create new dataframe to store points information
gs1 = pd.DataFrame(
    {'lat': ys,
    'lon': xs,
    'u_r': 'R'}) # rural indicator for use in DHS code

# Make into geodateframe by making geometry column from xs and ys
gs1 = gpd.GeoDataFrame(gs1, geometry=gpd.points_from_xy(xs,ys))

print(gs1)

# output to file
gs1.to_file('/home/s1891967/diss/Data/Output/AllRuralClust.shp')

# end time and calculate time taken
end = time.time()
print(end-start)