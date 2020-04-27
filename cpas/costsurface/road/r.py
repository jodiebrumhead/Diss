from osgeo import gdal, ogr
from sys import getsizeof
import os
import numpy as np
import pandas as pd
from fuzzywuzzy import process

# https://gis.stackexchange.com/questions/221718/rasterizing-shapefile-with-attribute-value-as-pixel-value-with-gdal-in-python
# https://www.datacamp.com/community/tutorials/fuzzy-string-python


# Filename of input shapefile
vector_fn = '/home/s1891967/diss/roads/AllRoads.shp'

# Excel file
costsfile = '/home/s1891967/diss/Road_Costs.csv'

# Output filename
raster_fn = '/home/s1891967/diss/All_roads.tif'


# Open the data source and read in the extent
source_ds = ogr.Open(vector_fn)
source_layer = source_ds.GetLayer()
x_min, x_max, y_min, y_max = source_layer.GetExtent()
feature = source_layer.GetNextFeature()

# Create the destination data source
pixel_size=0.00018518525
x_res = int((x_max - x_min) / pixel_size)
y_res = int((y_max - y_min) / pixel_size)
target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32) #without parsing field_vals to set getting number of all features from layer
target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))

# Array with distinct values of field 'Source' (Classes)
field_vals = set([feature.GetFieldAsString('tag') for feature in source_layer])

# Read excel file with walking speeds into pandas dataframe
costs = pd.read_csv(costsfile)

# Sort so quickest speed roads prioritised
# There may be more than one road per grid i.e. bridges etc... we will take the quickest one.... 
# Maybe should refine this to reduce speed where crossings.... 
# impact of congestion in urban areas... 
costs = costs.sort_values(by=['Walking_Speed'], ascending=True)

#possible to add option to remove paths from loop in here... 

arr1 = target_ds.GetRasterBand(1).ReadAsArray()
arr1 = np.where(arr1 == 0.0, np.NaN, arr1)

# Loop through road costs dataframe
for index, row in costs.iterrows():

    # match row[0] to field_vals
    match = process.extractOne(row[0], field_vals)

    sql_str = f"SELECT * FROM AllRoads WHERE tag='{match[0]}'"
    bv = row[1]

    opt = gdal.RasterizeOptions(burnValues=bv, allTouched=True, SQLStatement= sql_str, SQLDialect='SQLITE')

    gdal.Rasterize(target_ds, vector_fn, options=opt)

    arr = target_ds.GetRasterBand(1).ReadAsArray()

    arr = np.where(arr < 0.01, np.NaN, arr)

    x = np.isnan(arr1)
    arr1[x] = arr[x]


target_ds.GetRasterBand(1).WriteArray(arr)  # write image to the raster
target_ds.GetRasterBand(1).SetNoDataValue(-9999)  # set no data value
target_ds.FlushCache()  # write to disk
target_ds = None
    



# then loop through this ordered list to create raster and then array, can we do an in memory array... or do we need to do output to file?

# raster to rasterize into based on the resampling script.. i.e. we want the same value as the landcover layer.. 

# for each loop take the result of the last loop and add in the values from the new layer... 


#this should output one raster with road speed values per grid prioritised by roads where it is expected travale will be fastest
# this method would then work the same for different modes of transport even if the speed and prioritisations are in a different order


