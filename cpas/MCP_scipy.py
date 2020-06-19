"""Least Cost path utilising scipy"""

# http://tretherington.blogspot.com/2017/01/least-cost-modelling-with-python-using.html
# https://scikit-image.org/docs/0.7.0/api/skimage.graph.mcp.html

# Import packages
import numpy as np
from skimage import graph
from nlmpy import nlmpy

cs = np.array([[0, 0, 0, 0, 1, 1, 2, 3],
                [4, 4, 5, 5, 6, 6, 6, 6],
                [7, 8, 9, 10, 11, 12, 0, 0]])


def least_cost(cs, startCell, endCell):


    # Make any values below one equal to no data
    np.place(cs, cs < 1, -9999)
    # Specify the size of the cell
    #cellSize = 20

    # From the cost-surface create a 'landscape graph' object which can then be
    # analysed using least-cost modelling
    #lg = graph.MCP_Geometric(cs, sampling=(cellSize, cellSize))


    # Calculate the least-cost distance from the start cell to all other cells
    # [0] is returning the cumulative costs rather than the traceback
    # lcd = lg.find_costs(starts=[startCell])[0]

    # BUG: where do we tell the cell size


    route, cost = graph.mcp.route_through_array(cs, startCell, endCell, fully_connected = True, geometric = True)  # to find path and cost

    return route, cost


"""
# Export the data for comparison in GIS software
startGrid = np.zeros((101,101)) - 9999
startGrid[5,5] = 1
nlmpy.exportASCIIGrid("start.asc", startGrid, cellSize = 10)
nlmpy.exportASCIIGrid("cost-surface.asc", cs, cellSize = 10)
np.place(lcd, np.isinf(lcd), -9999) # insert no data values
nlmpy.exportASCIIGrid("least-cost-distances.asc", lcd, cellSize = 10)
"""