import sys

sys.path.append('/home/s1891967/diss/code/Diss/')

from cpas.tifs import *
import pandas as pd
import numpy as np

# https://stackoverflow.com/questions/34321025/replace-values-in-numpy-2d-array-based-on-pandas-dataframe


def lc_to_ws(arr, ws):

    # Read as dataframe
    costs = pd.read_csv(ws)
    # Extract codes and walking speeds
    oldval = np.array(costs['Code'])
    newval = np.array(costs['Walking Speed (km/h)'])

    # Change data type of land cover data
    arr = arr.astype(np.float64)

    # Replace land cover values with respective walking speeds
    mask = np.in1d(arr,oldval)
    idx = np.searchsorted(oldval,arr.ravel()[mask])
    arr.ravel()[mask] = newval[idx]
    mask.reshape(arr.shape)

    # nan values?
    arr = np.where(arr == 0.0, np.NaN, arr)

    return arr
