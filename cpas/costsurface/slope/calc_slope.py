# https://stackoverflow.com/questions/47653271/calculating-aspect-slope-in-python3-x-matlab-gradientm-function

from osgeo import gdal, osr, gdalconst
# Enable GDAL/OGR exceptions (enabling error messages)
gdal.UseExceptions()

"""
Function to calculate slope from DEM

N.B. not possible to output to temporary file as gdal.DEMprocessing errors if output is not a string.
"""

def calculate_gradient(inputDEM, outputstring):
    gdal.DEMProcessing(outputstring, inputDEM, 'slope', scale=111120)


if __name__ == '__main__':
    
    slope=calculate_gradient('/home/s1891967/diss/Uganda_SRTM30meters/Uganda_SRTM30meters.tif', '/home/s1891967/diss/resampleslope.tif')


