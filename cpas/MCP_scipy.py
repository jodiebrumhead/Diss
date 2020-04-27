"""Least Cost path utilising scipy"""

# http://tretherington.blogspot.com/2017/01/least-cost-modelling-with-python-using.html

# Import packages
import numpy as np
from skimage import graph
from nlmpy import nlmpy

# Set random seed so results are the same each time script runs
np.random.seed(1)

# Create a hypothetical cost-surface using the midpoint displacement method
cs = nlmpy.mpd(101, 101, h=1) * 5
# Make any values below one equal to no data
np.place(cs, cs < 1, -9999)
# Specify the size of the cell
cellSize = 10

# From the cost-surface create a 'landscape graph' object which can then be
# analysed using least-cost modelling
lg = graph.MCP_Geometric(cs, sampling=(cellSize, cellSize))


# Choose a starting cell location
startCell = (5, 5)

# Calculate the least-cost distance from the start cell to all other cells
lcd = lg.find_costs(starts=[startCell])[0]

# Export the data for comparison in GIS software
startGrid = np.zeros((101,101)) - 9999
startGrid[5,5] = 1
nlmpy.exportASCIIGrid("start.asc", startGrid, cellSize = 10)
nlmpy.exportASCIIGrid("cost-surface.asc", cs, cellSize = 10)
np.place(lcd, np.isinf(lcd), -9999) # insert no data values
nlmpy.exportASCIIGrid("least-cost-distances.asc", lcd, cellSize = 10)