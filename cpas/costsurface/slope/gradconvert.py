"""
Functions to remove too steep gradients and convert to slope %
"""

import numpy as np

def toosteep(arr):
    # Make nodata values and where steepness is over 45 degrees into NaN so not calculated
    arr1 = np.where(arr > 45, np.NaN, arr)
    arr2 = np.where(arr == -9999, np.NaN, arr1)
    return arr2


def gradtoslope(arr):
    arr1 = np.radians(arr) # convert from degrees to radians
    arr2 = np.tan(arr1) # calculate tan of radians
    arr3 = arr2 * 100 # calculate slope %
    return arr3
    

if __name__ == '__main__':

    arr = np.array([90, -9999, 50, 6, np.NaN, 45, 2])

    print(arr)

    arr = toosteep(arr)

    print(arr)

    arr = gradtoslope(arr)

    print(arr)