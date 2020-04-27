import sys
print(sys.path)

import cpas.costsurface.slope
from calc_slope import *
from Gradienteq import *
from gradconvert import *
from resample import *
from tifs import *


"""
All the processes needed to make DEM into speed impact for inclusion in cost surface.
"""

# Input DEM layer
SRTM30 = '/home/s1891967/diss/Uganda_SRTM30meters/Uganda_SRTM30meters.tif'

# Input Land Cover layer (for reference in resampling)
LC = '/home/s1891967/diss/UgandaLandCover/Uganda_Sentinel2_LULC2016.tif'

# Resample
print('Resampling...')
a = resamplefunc(SRTM30, LC)
print('Resample complete')

# Calculate Gradient (degrees)
print('Calculating gradients....')
calculate_gradient(a, outputstring='resampleslope.tif')
print('Gradients calculated')

# Read tiff back in 
print('Reading tiff....')
a = tiffHandle('resampleslope.tif')
a.readTiff('resampleslope.tif')
print('Tiff read')
print(a.data)

# Make over 45 degree slope no data
print('Removing steep values')
a.data = toosteep(a.data)
print(a.data)

# Convert to Slope (%)
print('Converting to slope...')
a.data = gradtoslope(a.data)
print(a.data)

# Calculate slope impact (%)
print('Calculating impact')
a.data = slopeimpact(a.data)
print(a.data)

#Write to tiff?
print('Writing to tiff')
a.writeTiff('slopeimpact.tif')










