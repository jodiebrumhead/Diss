"""
cs.py: A python script containing functions to convert walking speed into cost surfaces
"""

# Imports


def ws_to_cs(ws_surface, child_impact, res):
    """Convert walking speeds to a cost surface

    Parameters
    ----------
    ws_surface  : np.array
        The walking speeds surface
    child_impact : flt
        Percentage by which adult walking speeds are reduced to child walking speeds

    Returns
    -------
    cs
        Cost surface
    """

    # reduce by child impact
    arr = ws_surface*child_impact

    # convert from km/hour to m/s
    arr = arr*1000/3600

    # convert to time (seconds) from speeds
    # TODO: should this be the surface resolution rather than 20m
    cs = 20/arr

    return cs





