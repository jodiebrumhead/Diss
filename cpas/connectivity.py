# makes graph to show differences in contguity between 2 different layers. 

import tifs
import numpy as np
import matplotlib.pyplot as plt

# Functions
def limits(index, shp):
    if index < 0:
        return 0
    if index > shp:
        return shp
    return index

def connectivity_percents(data):
    w = 1
    ls = []
    # iterater
    for index, x in np.ndenumerate(data):
        if x != 0:
            # slice
            slc = data[limits(index[0]-w,data.shape[0]):limits(index[0]+w+1,data.shape[0]), limits(index[1]-w,data.shape[1]):limits(index[1]+w+1,data.shape[1])]
            # flatten
            slc = slc[~np.isnan(slc)]
            # count non- zero
            # account for edges... 
            c = (((np.count_nonzero(slc)/slc.shape[0])*9)) - 1
            # add to list
            ls.append(c)

    arr = np.array(ls)

    # round 
    arr = np.round(arr)

    unique, counts = np.unique(arr, return_counts=True)

    percents = (counts/counts.sum()) * 100

    return unique, percents

if __name__ == '__main__':
    # HRSL Raster
    hrsl_raster = "/home/s1891967/diss/Data/Input/Population/hrsl_Uganda.tif" # need to change these
    hrsl = tifs.tiffHandle(hrsl_raster)
    hrsl.readTiff(hrsl_raster)

    # GHSL Raster
    ghsl_raster = "/home/s1891967/diss/Data/Input/Population/ghsl_Uganda.tif" # need to change these
    ghsl = tifs.tiffHandle(ghsl_raster)
    ghsl.readTiff(ghsl_raster)

    hrsl.data = np.where(hrsl.data < 0, 0, hrsl.data)
    ghsl.data = np.where(ghsl.data < 0, 0, ghsl.data)


    hrsl_u, hrsl_p = connectivity_percents(hrsl.data)
    ghsl_u, ghsl_p = connectivity_percents(ghsl.data)

    print(hrsl_u, hrsl_p)
    print(ghsl_u, ghsl_p)

    plt.plot(hrsl_u ,hrsl_p, color='#0000ff', label='HRSL')
    plt.plot(ghsl_u, ghsl_p, color='#fde725', label='GHSL')


    plt.xlabel('Contiguity')
    plt.ylabel('Percent of Grid Squares')
    plt.legend()



    plt.savefig('/home/s1891967/diss/Data/Output/connectivity.png')


