"""
Resample DEM using landcover as reference
"""
# Code segements from 
# https://jgomezdans.github.io/gdal_notes/reprojection.html
# https://gis.stackexchange.com/questions/234022/resampling-a-raster-from-python-without-using-gdalwarp

from osgeo import gdal, gdalconst
# Enable GDAL/OGR exceptions (enabling error messages)
gdal.UseExceptions()

"""
Function to resample input file to match reference file. 

N.B. Has not been tested for reprojecting although should work for that also.
"""

def resamplefunc(inputfile, referencefile):

    # Gather input file information
    input = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
    inputProj = input.GetProjection()
    inputTrans = input.GetGeoTransform()
    datatype = input.GetRasterBand(1).DataType  # Data type

    # Gather reference file information
    reference = gdal.Open(referencefile, gdalconst.GA_ReadOnly)
    referenceProj = reference.GetProjection()
    referenceTrans = reference.GetGeoTransform()   
    x = reference.RasterXSize 
    y = reference.RasterYSize

    # Outputs
    driver = gdal.GetDriverByName('MEM') # Get in-memory driver
    output = driver.Create('',x,y,1,datatype) # Create raster in-memory of size x,y, 1 band, datatype from input layer
    output.SetGeoTransform(referenceTrans)
    output.SetProjection(referenceProj)
    o = output.ReadAsArray() # read into array to alter values
    o.fill(-9999) # 'MEM' driver initiates with 0's rather than -9999 for no data
    output.GetRasterBand(1).WriteArray(o) # write array back to GDAL object format in-memory
    output.GetRasterBand(1).SetNoDataValue(-9999)

    # Undertake resampling
    gdal.ReprojectImage(input, output, inputProj, referenceProj, gdalconst.GRA_Bilinear)

    # GDAL object returned by function
    return output



if __name__ == '__main__':

    # Run resample() function with input and reference .tif files.
    reprojected_dataset = resamplefunc('/home/s1891967/diss/Uganda_SRTM30meters/Uganda_SRTM30meters.tif', '/home/s1891967/diss/UgandaLandCover/Uganda_Sentinel2_LULC2016.tif')

    # To save as GeoTIFF.
    driver = gdal.GetDriverByName ( "GTiff" )
    dst_ds = driver.CreateCopy( '/home/s1891967/diss/resample.tif', reprojected_dataset, 0 )
    dst_ds = None # Flush the dataset to disk
    # Data is now saved.