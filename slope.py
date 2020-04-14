# https://stackoverflow.com/questions/47653271/calculating-aspect-slope-in-python3-x-matlab-gradientm-function

from osgeo import gdal
import numpy as np
import rasterio

def calculate_slope(DEM):
    gdal.DEMProcessing('slope.tif', DEM, 'slope')
    with rasterio.open('slope.tif') as dataset:
        slope=dataset.read(1)
    return slope

def calculate_aspect(DEM):
    gdal.DEMProcessing('aspect.tif', DEM, 'aspect')
    with rasterio.open('aspect.tif') as dataset:
        aspect=dataset.read(1)
    return aspect

slope=calculate_slope('DEM.tif')
aspect=calculate_aspect('DEM.tif')

print(type(slope))
print(slope.dtype)
print(slope.shape)
