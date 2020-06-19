
import datetime
import numpy as np
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

gdf = gpd.read_file('/home/s1891967/diss/Data/Output/cs_tests.shp')


# change formats

for index, row in gdf.iterrows():

    gdf.iloc[index, 5] = int(gdf.iloc[index, 5])

    gdf.iloc[index, 8] = pd.Timedelta((gdf.iloc[index, 8])+':00').total_seconds()
    gdf.iloc[index, 9] = pd.Timedelta((gdf.iloc[index, 9])+':00').total_seconds()


gdf['gm_mean'] = ((gdf['gm_there'] + gdf['gm_back'])/2).astype(np.float)

gdf['diff'] = (gdf['cost_adult'] - gdf['gm_mean']).astype(np.float)

gdf['norm_distance'] = (gdf['diff'] / ((gdf['cost_adult'] + gdf['gm_mean'])/2)).astype(np.float)

m = max([abs(max(gdf['norm_distance'])), abs(min(gdf['norm_distance']))])
print(m)

gdf['norm_1'] = gdf['norm_distance']/m


print(gdf['norm_1'])

"""
cost_adult = []
gm_mean = []
diff = []

for index, rox in gdf.iterrows():
    cost_adult.append(gdf.iloc[index, 5])
    gm_mean.append(gdf.iloc[index, 11])
    diff.append(gdf.iloc[index, 12])

print(cost_adult)
print(gm_mean)
print(diff)
"""

x = [0,15000]
y = [0,15000]

n = max([abs(max(gdf['norm_1'])), abs(min(gdf['norm_1']))])
print(n)

#offset = mcolors.TwoSlopeNorm(vcenter=0)
#norm_c = offset(gdf['norm_distance'])

cmap = mcolors.ListedColormap(sns.diverging_palette(145, 280, s=100, l=25, n=1000))

plt.plot(x,y, '-', color='#b3b6b7', alpha=0.4)
plt.scatter(gdf['cost_adult'], gdf['gm_mean'], norm=mcolors.TwoSlopeNorm(0), c=gdf['norm_1'], cmap=cmap)

for i in range(20):
    plt.annotate(i, (gdf['cost_adult'].iloc[i]+400, gdf['gm_mean'].iloc[i]-200), fontsize=5)

plt.xlabel('Cost Surface Time (seconds)')
plt.ylabel('Google Maps Time (seconds)')
plt.axis('scaled')

plt.grid(alpha=0.2)


cbar = plt.colorbar()
cbar.set_label('Normalised Difference')

plt.savefig('/home/s1891967/diss/Data/Output/cs_tests.png')

gdf['label'] = gdf.index

gdf.to_file('/home/s1891967/diss/Data/Output/cs_tests.shp')


