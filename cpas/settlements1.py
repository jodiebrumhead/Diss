from osgeo import gdal, ogr, osr
import rasterstats as rs
import geopandas as gpd
import pandas as pd
import numpy as np
import sys
from sklearn import cluster, neighbors, metrics
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import tifs
gdal.UseExceptions()

import geopandas as gpd

# https://gis.stackexchange.com/questions/321021/splitting-polygon-into-equal-area-polygons-in-qgis-3
# https://stackoverflow.com/questions/33440530/identify-unique-groupings-of-polygons-in-geopandas-shapely


raster = "/home/s1891967/diss/Data/Input/hrsl_settlement/hrsl_uga_pop.tif"

r = tifs.tiffHandle(raster)
r.readTiff(raster)


# Make -1 no data values 0
r.data = np.where(r.data < 0, 0, r.data)
# Identify index of pixels which are not zero i.e. have a population
pop_indices = np.transpose(np.nonzero(r.data))


# Nearest neighbour graphs for estimating DBSCAN epsilon
nbrs = neighbors.NearestNeighbors(n_neighbors=20, algorithm='auto', metric='euclidean').fit(pop_indices)
distances, indices = nbrs.kneighbors(pop_indices)
fourth_nnd = [distances[i][19] for i in range(len(distances))]
fourth_nnd.sort()
plt.plot(fourth_nnd)
plt.savefig('/home/s1891967/diss/Data/Output/eps.png')


# DBSCAN parmeters
EPS_DISTANCE = 10
MIN_SAMPLE_POLYGONS = 15

# Undertake DBSCAN clustering
dbscan = cluster.DBSCAN(eps=EPS_DISTANCE, min_samples=MIN_SAMPLE_POLYGONS)
clusters = dbscan.fit(pop_indices)

# Create array of cluster labels
# As 0 is a cluster label make 0 values in original dataset into null values
r.data = np.where(r.data == 0.0, np.NaN, r.data)

for i,j in zip(pop_indices,clusters.labels_):
        a,b = i[0],i[1]
        r.data[a,b] = j


r.data = r.data + 1

# Output tif of clusters
cluster_raster = '/home/s1891967/diss/Data/Output/final_test_1.tif'
r.writeTiff(cluster_raster)


print(metrics.silhouette_score(pop_indices, clusters.labels_))

"""

######################################################################################

# Polygonize the clusters

# open raster
src_ds = gdal.Open(cluster_raster)
srcband = src_ds.GetRasterBand(1)
band_arr = srcband.ReadAsArray()

# getting projection from source raster
srs = osr.SpatialReference()
srs.ImportFromWkt(src_ds.GetProjectionRef())

# Create polygons
dst_layername = "final_test_2"
drv = ogr.GetDriverByName("ESRI Shapefile")
dst_ds = drv.CreateDataSource("/home/s1891967/diss/Data/Output/" + dst_layername + ".shp" )
dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)

newField = ogr.FieldDefn('DN', ogr.OFTInteger)
dst_layer.CreateField(newField)

# Undertake polygonization 
gdal.Polygonize(srcband, srcband, dst_layer, 0, [], callback=None )

# Clear memory so shapefile can be reopened
dst_ds = None


# TODO: Does this allow multipart polygons



###################################################################################

# Undertake raster stats for the cluster polygons to find population per cluster

#  Open shapefile
shapefile = '/home/s1891967/diss/Data/Output/final_test_2.shp'
df = gpd.read_file(shapefile)

# TODO: polygon to multipolygon

print(df)

a = df['DN']

# need to get list of numbers in this column and then somehow loop through it ... making polygons into multipolygons

s = rs.zonal_stats(shapefile, raster, geojson_out=True, nodata=-1, stats="sum")

df = gpd.GeoDataFrame.from_features(s)


###################################################################################

# from polygons identify DHS clusters based on population size

def poly_to_cluster(row, r):
        bounds = row.geometry.bounds

        width = bounds[2]-bounds[0]
        height = bounds[3]-bounds[1]

        pointsacross = round(width/r.pixelWidth)
        pointsdown = round(height/r.pixelHeight)

        # Create list of central points for each pixel within bounds
        l = [(bounds[0]+n*r.pixelWidth+0.5*r.pixelWidth, bounds[3] + m*r.pixelHeight+0.5*r.pixelHeight) for n in range(pointsacross) for m in range(abs(pointsdown))]

        # make into x list and y list
        x, y = map(list, zip(*l))

        # make into geoseries of points
        gs = gpd.GeoSeries(gpd.points_from_xy(x,y))

        # Remove points which are not within the geometry of the polygon
        pip_mask = gs.within(row.geometry)
        gs = gs.loc[pip_mask]

        # create array of remaining points
        array = np.array([[v.x, v.y] for v in gs])

        # Undertake k means clustering on regular points within polygon
        kmeans = cluster.KMeans(n_clusters=int(round(row['sum'], -2)//100), random_state=0).fit(array)

        # Return the x,y, for the centres of each cluster
        return kmeans.cluster_centers_.tolist()



# For each settlement polygon
clusters = []

for index, row in df.iterrows():
    if row['sum'] > 100:
        clusters.append(poly_to_cluster(row, r))
    # TODO: add other options for if?

# Flatten to get list of points for all settlements
flatter = [val for sublist in clusters for val in sublist]

# Turn list of points into geoseries so it can be exported as shapefile
x1, y1 = map(list, zip(*flatter))
gs1 = gpd.GeoSeries(gpd.points_from_xy(x1,y1))


gs1.to_file('/home/s1891967/diss/Data/Output/final_test_3.shp')


# TODO: Something about the CRS

"""