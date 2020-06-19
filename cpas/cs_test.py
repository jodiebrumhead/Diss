"""
cs_test.py: A python script to produce test output shapefiles of costs and routes derived from the cost surface

Inspiration from:
https://www.earthdatascience.org/courses/use-data-open-source-python/spatial-data-applications/lidar-remote-sensing-uncertainty/extract-data-from-raster/
"""

#Imports
import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
from MCP_scipy import least_cost
from shapely.geometry import LineString

import tifs


def clean_invalid_loc(gdf, tif):
    """Remove points outside cost surface extent

    Parameters
    ----------
    gdf : GeoDataFrame
        Dataset to remove invalid locations from
    tif : object
        cost surface object read from GeoTiff

    Returns
    -------
    gdf
        GeoDataFrame cleaned of invalid locations
    """

    baddata = []

    # for each row find if row point is outside tif extent
    # if so then append to list to remove later
    for index, row in gdf.iterrows():
        if tif.xOrigin > row.geometry.x:
            baddata.append(index)
        elif tif.xOrigin+tif.pixelWidth*tif.data.shape[1] < row.geometry.x:
            baddata.append(index)
        elif tif.yOrigin < row.geometry.y:
            baddata.append(index)
        elif tif.yOrigin+tif.pixelHeight*tif.data.shape[0] > row.geometry.y:
            baddata.append(index)   

    # remove data from geodataframe based on list
    gdf = gdf.drop(gdf.index[baddata])

    return gdf


def find_pixel(sample, tif):
    """To find the numpy reference for a co-ordinate

    Parameters
    ----------
    sample : GeoDataFrame
        A singular row 
    tif : object
        cost surface object read from GeoTiff

    Returns
    -------
    yInds, xInds : Tuple
        Numpy pixel reference of coordinates
    """

    xInds=(((sample.geometry.x.values[0]-tif.xOrigin))//tif.pixelWidth).astype(int)  # determine which pixels the data lies in
    yInds=((tif.yOrigin - sample.geometry.y.values[0])//-tif.pixelHeight).astype(int) # determine which pixels the data lies in
    return (yInds, xInds) # how you reference an array dimensions and elements

def find_coord(x_ls, y_ls, tif):
    """To find the coordinates for a numpy pixel reference

    Parameters
    ----------
    x_ls : list
        X pixel numpy references
    y_ls : list
        Y pixel numpy references    
    tif : object
        cost surface object read from GeoTiff

    Returns
    -------
    xCoord : numpy.ndarray
        Array of coordinates
    yCoord : numpy.ndarray
        Array of coordinates
    """

    xCoord = np.asarray(x_ls)*tif.pixelWidth+tif.xOrigin
    yCoord = np.asarray(y_ls)*tif.pixelHeight+tif.yOrigin

    return xCoord, yCoord


if __name__ == '__main__':

    # Read in point shapefiles as geodataframes
    dhs_inp = '/home/s1891967/diss/Data/Input/Uganda_DHSloc/Uganda_DHSloc.shp'
    dhs = gpd.read_file(dhs_inp)

    health_inp = '/home/s1891967/diss/Data/Input/Health/UgandaClinics.shp'
    health = gpd.read_file(health_inp)

    # Read in Cost surface
    inp = '/home/s1891967/diss/Data/Output/costsurface2.tif'
    tiff_attributes = tifs.tiffHandle(inp)
    tiff_attributes.readTiff(inp)

    # Clean both dhs and health datasets for invalid locations
    dhs = clean_invalid_loc(dhs, tiff_attributes)
    health = clean_invalid_loc(health, tiff_attributes)

    # Creating an empty GeoDataframe using CRS from dhs shapefile
    gdfObj = gpd.GeoDataFrame(columns=['dhs_x', 'dhs_y', 'health_x','health_y', 'cost_sec', 'cost_adult', 'cost_t', 'gm_str', 'geometry'], geometry='geometry', crs=dhs.crs)

    # While loop to control number of samples wanted
    while len(gdfObj.index) < 20:
        dhs_sample = dhs.sample() # random sample row from gdf
        dhs_pixel = find_pixel(dhs_sample, tiff_attributes) # find numpy array pixel ref for coords

        health_sample = health.sample() # repeat for health
        health_pixel = find_pixel(health_sample, tiff_attributes) # repeat for health

        # find the difference between the pixels
        y_diff = abs(dhs_pixel[0]-health_pixel[0])
        x_diff = abs(dhs_pixel[1]-health_pixel[1])

        # only undertake LCP analysis if points not too far from each other
        if y_diff < 500 and x_diff < 500:
            
            # LCP analysis returning the route and cost of route
            r, c = least_cost(tiff_attributes.data, dhs_pixel, health_pixel)

            # route returned as list of tuples referencing array pixel
            y_ls, x_ls = map(list, zip(*r)) # unpack route list of tuples into 2 lists
            xs, ys = find_coord(x_ls, y_ls,tiff_attributes) # convert pixel references to coords
            line = LineString(list(zip(xs, ys))) # create geometric linestring object from lists of coords

            # add translations to cost? into minutes and remove 22%
            c1 = c*0.78
            t = str(datetime.timedelta(seconds=int(c*0.78)))

            # Append details of sampled points, route and cost to gdf
            gdfObj = gdfObj.append({'dhs_x': dhs_sample.geometry.x.values[0], 'dhs_y': dhs_sample.geometry.y.values[0],
             'health_x': health_sample.geometry.x.values[0], 'health_y': health_sample.geometry.y.values[0],
             'cost_sec': c, 
             'cost_t': t,
             'cost_adult' : c1,
             'gm_str': f'www.google.com/maps/dir/{round(dhs_sample.geometry.y.values[0], 7)},{round(dhs_sample.geometry.x.values[0], 7)}/{round(health_sample.geometry.y.values[0], 7)},{round(health_sample.geometry.x.values[0], 7)}/data=!3m2!1e3!4b1!4m2!4m1!3e2',
             'geometry': line},
             ignore_index=True)

        else:
            pass


#gdfObj.to_file('/home/s1891967/diss/Data/Output/cs_tests.shp')


