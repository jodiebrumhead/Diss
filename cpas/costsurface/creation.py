

"""
A python script to create a cost surface from land cover, road and DEM datasets
"""


"""Inputs and Outputs"""

#path to files
p = '/home/s1891967/diss/Data/Input/'

# Landcover
lc_inp = p + 'UgandaLandCover/Uganda_Sentinel2_LULC2016.tif'
# Roads
r_inp = p + 'roads/AllRoads.shp'
# DEM
dem_inp = p + 'Uganda_SRTM30meters/Uganda_SRTM30meters.tif'

# Walking Speeds
lc_ws = p + 'Landcover_Costs.csv'
r_ws = p + 'Road_Costs.csv'

# Output
cs_out = '/home/s1891967/diss/Data/Output/costsurface.tif'


"""Processes"""

# Get tiff attributes from land cover file, these will be used for other processes
tiff_attributes = tiffHandle(lc_inp)
tiff_attributes.readTiff(lc_inp)

# Extract land cover data 
land_cover = tiff_attributes.data

# Convert land cover to walking speeds
land_cover = lc_to_ws(land_cover, lc_ws)

# Convert roads to walking speeds
roads = r_to_ws(r_inp, r_ws, tiff_attributes)

# Combine roads and landcover walking speeds to make one surface
ws_surface = backfill(roads, land_cover)

# Create slope impact surface
slope_impact = dem_to_slope_impact(dem_inp, tiff_attributes)

# Include impact of slope in walking speeds surface
ws_surface = ws_surface*slope_impact

# Convert walking speed surface to a cost surface
cost_surface = ws_to_c(ws_surface)


# Output to tiff
tiff_attributes.data = cost_surface
tiff_attributes.writeTiff(cs_out)