from osgeo import gdal, gdalconst, osr
# Enable GDAL/OGR exceptions
gdal.UseExceptions()

#https://jgomezdans.github.io/gdal_notes/reprojection.html

def reproject_dataset ( dataset, \
            pixel_spacing=0.00018518525, epsg_from=4326, epsg_to=4326 ):
    """
    A sample function to reproject and resample a GDAL dataset from within 
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:
    
    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners 
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """
    # Define the UK OSNG, see <http://spatialreference.org/ref/epsg/27700/>
    t = osr.SpatialReference ()
    t.ImportFromEPSG ( epsg_to )
    f = osr.SpatialReference ()
    f.ImportFromEPSG ( epsg_from )
    tx = osr.CoordinateTransformation ( f, t )
    # Up to here, all  the projection have been defined, as well as a 
    # transformation from the from to the  to :)
    # We now open the dataset
    g = gdal.Open ( dataset )
    # Get the Geotransform vector
    geo_t = g.GetGeoTransform ()
    x_size = g.RasterXSize # Raster xsize
    y_size = g.RasterYSize # Raster ysize
    # Work out the boundaries of the new dataset in the target projection
    (ulx, uly, ulz ) = tx.TransformPoint( geo_t[0], geo_t[3])
    (lrx, lry, lrz ) = tx.TransformPoint( geo_t[0] + geo_t[1]*x_size, \
                                          geo_t[3] + geo_t[5]*y_size )
    print(ulx, uly, ulz )
    print(lrx, lry, lrz )
    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName( 'MEM' )
    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    dest = mem_drv.Create('', int((lrx - ulx)/pixel_spacing), \
            int((uly - lry)/pixel_spacing), 1, gdal.GDT_Float32)
    # Calculate the new geotransform
    new_geo = ( ulx, pixel_spacing, geo_t[2], \
                uly, geo_t[4], -pixel_spacing )
    # Set the geotransform
    dest.SetGeoTransform( new_geo )
    dest.SetProjection ( t.ExportToWkt() )
    # Perform the projection/resampling 
    res = gdal.ReprojectImage( g, dest, \
                f.ExportToWkt(), t.ExportToWkt(), \
                gdal.GRA_Bilinear )
    return dest

if __name__ == '__main__':

        # Now, reproject and resample the NDVI dataset
    reprojected_dataset = reproject_dataset ('/home/s1891967/diss/Uganda_SRTM30meters/Uganda_SRTM30meters.tif')
    # This is a GDAL object. We can read it
    reprojected_data = reprojected_dataset.ReadAsArray ()
    # Let's save it as a GeoTIFF.
    driver = gdal.GetDriverByName ( "GTiff" )
    dst_ds = driver.CreateCopy( '/home/s1891967/diss/reproj.tif', reprojected_dataset, 0 )
    dst_ds = None # Flush the dataset to disk
    # Data is now sav