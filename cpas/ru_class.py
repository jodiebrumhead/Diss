import tifs
import numpy as np
from osgeo import gdal, gdalconst
gdal.UseExceptions()



lc_filepath = '/home/s1891967/diss/Data/Input/UgandaLandCover/Uganda_Sentinel2_LULC2016.tif'

hrsl_filepath = "/home/s1891967/diss/Data/Input/hrsl_settlement/hrsl_uga_pop.tif"

hrsl = tifs.tiffHandle(hrsl_filepath)
hrsl.readTiff(hrsl_filepath)

hrsl.emptyTiff()


# Use water from landcover data to make mask
# Resample to 30m resolution
inp = gdal.Open(lc_filepath, gdalconst.GA_ReadOnly)
inputProj = inp.GetProjection()
inputTrans = inp.GetGeoTransform()

gdal.ReprojectImage(inp, hrsl.dst_ds, inputProj, hrsl.proj, gdalconst.GRA_NearestNeighbour)

lc_resampled = hrsl.dst_ds.GetRasterBand(1).ReadAsArray()


# Where water make null value
hrsl.data = np.where(lc_resampled == 10, np.NaN, hrsl.data)


# where not in Uganda make null value
hrsl.data = np.where(lc_resampled == lc_resampled, hrsl.data, np.NaN)


# where no population make 0 
hrsl.data = np.where(hrsl.data < 0, 0, hrsl.data)

hrsl.data = np.round(hrsl.data, 2)


# hrsl.data where cell classified as urban remove from dataset
# would need to hrsl.data.copy() to avoid wrongly classifying
new_hrsl = hrsl.data.copy()

def limits(index, shp):
    if index < 0:
        return 0
    if index > shp:
        return shp
    return index

def connectivity(s):
    c = np.count_nonzero(s)/s.shape[0]
    if c > 0.5: # TODO: need to confirm this number
        return True
    return False

def popdens(s):
    pd = s.sum()/(s.shape[0] * 30 * 30)
    if pd > 0.0003: # TODO: need to confirm this number
        return True
    return False

w = 2 # TODO: need to confirm this number

# for each pixel
for index, value in np.ndenumerate(hrsl.data):
    if value != value:
        pass
    elif value == 0:
        pass
    else:
        # slice
        slc = hrsl.data[limits(index[0]-w,new_hrsl.shape[0]):limits(index[0]+w+1,new_hrsl.shape[0]), limits(index[1]-w,new_hrsl.shape[1]):limits(index[1]+w+1,new_hrsl.shape[1])]
        # flatten slice and remove NaNs
        slc = slc[~np.isnan(slc)]
        # 2 statements which need to evaluate to true funtions?
        if connectivity(slc) and popdens(slc): # if urban then replace pop with 0 as do not want it to be used in clustering
            new_hrsl[index] = 0
            print(f'{index} value changed')


hrsl.data = new_hrsl

hrsl.writeTiff('/home/s1891967/diss/Data/Output/RU_test.tif')







