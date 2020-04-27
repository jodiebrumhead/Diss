from osgeo import gdal, ogr
from sys import getsizeof
import os
import sys
import numpy as np

np.set_printoptions(threshold=sys.maxsize)

# Enable GDAL/OGR exceptions
gdal.UseExceptions()


# Filename of input shapefile
vector_fn = '/home/s1891967/diss/Test_roads.shp'

raster_fn = '/home/s1891967/diss/Test_roads.tif'

# Open the data source and read in the extent
source_ds = ogr.Open(vector_fn)
source_layer = source_ds.GetLayer()
x_min, x_max, y_min, y_max = source_layer.GetExtent()
feature = source_layer.GetNextFeature()

print(x_min, x_max, y_min, y_max)
pixel_size=0.00018518525

# Create the destination data source
x_res = int((x_max - x_min) / pixel_size)
y_res = int((y_max - y_min) / pixel_size)
target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32) #without parsing field_vals to set getting number of all features from layer
target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))

# Array with distinct values of field 'Source' (Classes)
field_vals = set([feature.GetFieldAsString('tag') for feature in source_layer])

arr1 = target_ds.GetRasterBand(1).ReadAsArray()
arr1 = np.where(arr1 == 0.0, np.NaN, arr1)

bv=0

for i in field_vals:

    sql_str = f"SELECT * FROM Test_roads WHERE tag='{i}'"
    print(sql_str)
    bv = bv+10

    opt = gdal.RasterizeOptions(burnValues=bv, allTouched=True, SQLStatement= sql_str, SQLDialect='SQLITE')

    gdal.Rasterize(target_ds, vector_fn, options=opt)

    arr = target_ds.GetRasterBand(1).ReadAsArray()

    arr = np.where(arr < 1, np.NaN, arr)

    x = np.isnan(arr1)
    arr1[x] = arr[x]


target_ds.GetRasterBand(1).WriteArray(arr)  # write image to the raster
target_ds.GetRasterBand(1).SetNoDataValue(-9999)  # set no data value
target_ds.FlushCache()  # write to disk
target_ds = None