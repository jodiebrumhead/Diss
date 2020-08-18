"""
A function to return True if a cluster is RURAL according to Degree of Urbanization parameters
"""

# Imports
import numpy as np
import alphashape
from shapely.geometry import Point


def rural_test(arr, clus_indices, pop_total):
    """
    Tests whether a cluster is rural or urban

    Parameters
    ----------
    arr : numpy array
        HRSL data
    clus_indices : numpy array
        Numpy array of cluster indices 
    pop_total : float
        Population total of the cluster

    Returns
    -------
    Boolean Value
    """
    # check population total first
    if pop_total < 5000:
        return True # return True when Rural
    if pop_total > 50000:
        return False # return False when Urban

    # else if within 5000 and 50000

    # Create concave hull for cluster
    alpha = 0.95 * alphashape.optimizealpha(clus_indices)
    hull = alphashape.alphashape(clus_indices, alpha)

    # Find bounding box
    bbox = hull.bounds
    # Find possible indexes within bounding box
    bbox_poss_ind = [(i,j) for i in range(int(bbox[0]), int(bbox[2]+1)) for j in range(int(bbox[1]), int(bbox[3]+1))]
    # Find where indexes intersect (want boundary ones too) concave hull
    clus_area_inds = [p for p in bbox_poss_ind if hull.intersects((Point(p)))]


    # Find all values within concave hull of cluster importantly the 0s too
    clus_values = arr[clus_area_inds]

    # Remove NaNs as we do not want to consider these in pop density calc
    # as they are water or outside Uganda
    clus_values = clus_values[~np.isnan(clus_values)]

    # test population density
    if clus_values.sum()/(clus_values.shape[0] * 30 * 30) < 0.0003: 
        return True # return True when rural 
    else:
        return False # return False when urban
















