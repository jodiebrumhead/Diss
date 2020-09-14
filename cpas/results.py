import geopandas as gpd
import geopy.distance
from shapely.geometry import Polygon
from sklearn.metrics import mean_squared_error
from rasterstats import zonal_stats
import numpy as np
import math
import time

import tifs
import buf

start = time.time()

# import access services grid
access_fn = '/home/s1891967/diss/Data/Output/ServiceArea.tif'
access = tifs.tiffHandle(access_fn)
access.readTiff(access_fn)

# import rural dhs points
potent_clust_fn = '/home/s1891967/diss/Data/Output/AllRuralClust.shp'
potent_clust = gpd.read_file(potent_clust_fn)

# import displaced points
potent_clust_dis_fn = '/home/s1891967/diss/Data/Output/Displaced10.shp'
potent_clust_dis = gpd.read_file(potent_clust_dis_fn)

# migrate displaced point lat and lon to original points for comaparison
potent_clust['dis_lat'] = potent_clust_dis['lat']
potent_clust['dis_lon'] = potent_clust_dis['lon']

# remove non displaced points
potent_clust_remove = potent_clust.query('(lon == dis_lon) and (lat == dis_lat)')
potent_clust = potent_clust.drop(potent_clust_remove.index)
potent_clust_dis = potent_clust_dis.drop(potent_clust_remove.index)


# find pixel ref 
potent_clust['xInds'] = (((potent_clust.lon-access.xOrigin))/access.pixelWidth).astype(int)
potent_clust['yInds'] = ((access.yOrigin - potent_clust.lat)/-access.pixelHeight).astype(int)

potent_clust['xInds_dis'] = (((potent_clust.dis_lon-access.xOrigin))/access.pixelWidth).astype(int)
potent_clust['yInds_dis'] = ((access.yOrigin - potent_clust.dis_lat)/-access.pixelHeight).astype(int)

# remove those outside access layer bounds
potent_clust_remove = potent_clust.query('(xInds > @access.nX) or (xInds_dis > @access.nX) or (yInds > @access.nY) or (yInds_dis > @access.nY)')
potent_clust = potent_clust.drop(potent_clust_remove.index)
potent_clust_dis = potent_clust_dis.drop(potent_clust_remove.index)
# TODO: add print to see if there are being removed... 


# find time to access for undisplaced and displaced
potent_clust['Access'] = access.data[potent_clust['yInds'], potent_clust['xInds']]
potent_clust['Access_dis'] = access.data[potent_clust['yInds_dis'], potent_clust['xInds_dis']]


# remove where either of these columns are nan... 
potent_clust_remove = potent_clust.query('(Access != Access) or (Access_dis != Access_dis)')
potent_clust = potent_clust.drop(potent_clust_remove.index)
potent_clust_dis = potent_clust_dis.drop(potent_clust_remove.index)
# TODO: add print... 


# find distance between points and displaced points 
distance_diff = [geopy.distance.distance((row.lat, row.lon),(row.dis_lat, row.dis_lon)).km for _, row in potent_clust.iterrows()]
potent_clust['Distance_displaced'] = distance_diff

#confusion matrix
#conf_matrix = potent_clust.query('(Access < 3600 and Access_dis < 3600) or (Access > 3600 and Access_dis > 3600)')

"""
# Maximum possible displacement error 
potent_clust_poly = potent_clust.copy()

buffer = []

# create buffer for each point
for index, row in potent_clust_poly.iterrows():
    buffer.append(Polygon(buf.geodesic_point_buffer(row.lat, row.lon, 5)))

potent_clust_poly.geometry = buffer

# undertake zonal stats within the buffer
zs = zonal_stats("/home/s1891967/diss/Data/Output/polys.shp", "/home/s1891967/diss/Data/Output/ServiceArea.tif", geojson_out=True, copy_properties=True, stats="min max mean")

zs_df = gpd.GeoDataFrame.from_features(zs)
potent_clust = potent_clust.reset_index()

# Function to determine whether min or max is furthest from the original point
def fun(row):
    a = abs(row['max']-row['Access'])
    b = abs(row['min']-row['Access'])
    return max(a,b)

potent_clust['max_error'] = zs_df.apply(fun, axis=1)

potent_clust['mean_error'] = abs(zs_df['mean'] - zs_df['Access'])

potent_clust.to_file("/home/s1891967/diss/Data/Output/potential_errors.shp")
"""

# Applying methods A and B

# create empty lists for filling
within_5 = []
within_5_access = []
stddev = []
within_5_mean = []
within_5_min = []
within_5_max = []

nearest = []
nearest_access = []


# for each displaced point
for index, row in potent_clust_dis.iterrows():

    print(row)

    # Create a 5 km buffer
    buffer = Polygon(buf.geodesic_point_buffer(row.lat, row.lon, 5))
    # Find undisplaced points within the buffer and create boolean mask
    pip_mask = potent_clust.within(buffer)
    # apply this to undisplaced points to get the index of the points
    pip_data = potent_clust.loc[pip_mask].index.values

    if len(pip_data) > 0:

        within_5.append(pip_data) # add to list
        # from indexes of undisplaced points within buffer find the already measured access
        access = potent_clust.loc[pip_data, ['Access']].values
        within_5_access.append(access) # add to list

        # Analysis of access for points within 5km 
        within_5_mean.append(access.mean()) # calculate mean
        within_5_min.append(access.min()) # calculate minimum
        within_5_max.append(access.max()) # calculate maximum
        stddev.append(access.std()) # calculate standard deviation

        # Finding the undisplaced point nearest to the displaced point
        dist = 5
        pnt = index

        displaced_coords = (row.lat, row.lon)

        for i in pip_data:
            undisplaced_coords = (potent_clust.loc[i, ['lat']].values[0], potent_clust.loc[i, ['lon']].values[0])
            d = geopy.distance.distance(displaced_coords, undisplaced_coords).km
            if d < dist:
                dist = d
                pnt = i

        nearest.append(pnt)
        nearest_access.append(potent_clust.loc[pnt, ['Access']].values[0])
        
    else:
        within_5.append(np.NaN)
        within_5_access.append(np.NaN)
        stddev.append(np.NaN)
        within_5_mean.append(np.NaN)
        within_5_min.append(np.NaN)
        within_5_max.append(np.NaN)

        nearest.append(np.NaN)
        nearest_access.append(np.NaN)


# add results to dataframe
#potent_clust['within_5'] = within_5
potent_clust['within_5_access'] = within_5_access
potent_clust['within_5_min'] = within_5_min
potent_clust['within_5_mean'] = within_5_mean
potent_clust['within_5_max'] = within_5_max
potent_clust['within_5_stddev'] = stddev

potent_clust['Nearest'] = nearest
potent_clust['Nearest_access'] = nearest_access

# edit so format exportable into shapefile
potent_clust['within_5_access'] = potent_clust['within_5_access'].astype(str).str.replace('\n', ',')
potent_clust['within_5_access'] = potent_clust['within_5_access'].str.replace('[', '')
potent_clust['within_5_access'] = potent_clust['within_5_access'].str.replace(']', '')


# Calculating results
# TODO: dividing by 0 leads to infinity.... 

# finding error
potent_clust['dis_er'] = potent_clust['Access_dis']-potent_clust['Access']
potent_clust['near_er'] = potent_clust['Nearest_access']-potent_clust['Access']
potent_clust['buf_er'] = potent_clust['within_5_mean']-potent_clust['Access']

# finding percentage error 
potent_clust['dis_pe'] = ((abs(potent_clust['dis_er']))/potent_clust['Access']) * 100
potent_clust['near_pe'] = ((abs(potent_clust['near_er']))/potent_clust['Access']) * 100
potent_clust['buf_pe'] = ((abs(potent_clust['buf_er']))/potent_clust['Access']) * 100

# count number of times nearest = index... 
potent_clust['index'] = potent_clust.index.values
potent_clust['near_count'] = potent_clust['index'] - potent_clust['Nearest']
prcnt = (np.count_nonzero(potent_clust['near_count'])/len(potent_clust.index)) * 100

# drop unneeded columns
potent_clust = potent_clust.drop(columns = ['xInds', 'yInds', 'xInds_dis', 'yInds_dis', 'near_count', 'Nearest'])

# Output to shapefile
potent_clust.to_file("/home/s1891967/diss/Data/Output/results_displaced10.shp")

# Create report
a = f'Input filename: {potent_clust_dis_fn} \n'

# change infinity to null so does not impact calcs
potent_clust = potent_clust.replace([np.inf, -np.inf], np.nan)

b = f'Mean error for displaced points: {potent_clust.dis_er.mean(skipna=True)}\n'
c = f'Mean percentage error for displaced points: {potent_clust.dis_pe.mean(skipna=True)}\n'
d = f'RMSE for displaced points: {math.sqrt(((potent_clust.dis_er ** 2).sum())/len(potent_clust.dis_er))}\n'

print(d)

e = f'Mean error for displaced points when access measured from nearest settlement: {potent_clust.near_er.mean(skipna=True)}\n'
f = f'Mean percentage error for displaced points when access measured from nearest settlement: {potent_clust.near_pe.mean(skipna=True)}\n'
g = f'RMSE for displaced points when access measured from nearest settlement: {math.sqrt(((potent_clust.near_er ** 2).sum())/len(potent_clust.near_er))}\n'

h = f'Mean error for displaced points when access measured from all settlements with 5km of displaced point: {potent_clust.buf_er.mean(skipna=True)}\n'
i = f'Mean percentage error for displaced points when access measured from all settlements with 5km of displaced point: {potent_clust.buf_pe.mean(skipna=True)}\n'
j = f'RMSE for displaced points when access measured from all settlements with 5km of displaced point: {math.sqrt(((potent_clust.buf_er ** 2).sum())/len(potent_clust.buf_er))}\n'




k = f'Percentage of displaced points for which the nearest settlement is not the original settlement: {prcnt}\n'

# end time and calculate time taken
end = time.time()
t = end-start
l = f'Time taken: {t}'

report =  a + b + c + d + e + f + g + h + i + j + k + l

report_fn = '/home/s1891967/diss/Data/Output/results_displaced10.txt'
with open(report_fn, 'w') as rfn:
    rfn.write(report)

