import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sfg
import numpy as np
import time
import scipy

# Script to make graphs of displacement error, calculate medians and t-tests

results_fn = "/home/s1891967/diss/Data/Output/results_fin.shp"
results = gpd.read_file(results_fn)


results_10_fn = "/home/s1891967/diss/Data/Output/results_10.shp"
results_10 = gpd.read_file(results_10_fn)


p1 = sns.jointplot(x=results['Distance_d'], y=results['dis_er'], kind='scatter', s=0.2).set_axis_labels("Distance displaced (km)", "Error when measured from displaced point (seconds)")
p1.ax_marg_y.set_ylim(results['dis_er'].min(), results['dis_er'].max())


p2 = sns.jointplot(x=results['Distance_d'], y=results['near_er'], kind='scatter', s=0.2).set_axis_labels("Distance displaced (km)", "Error when measured from nearest settlement (seconds)")
p2.ax_marg_y.set_ylim(results['dis_er'].min(), results['dis_er'].max())


p3 = sns.jointplot(x=results['Distance_d'], y=results['buf_er'], kind='scatter', s=0.2).set_axis_labels("Distance displaced (km)", "Error when measured using 5km buffer (seconds)")
p3.ax_marg_y.set_ylim(results['dis_er'].min(), results['dis_er'].max())

p4 = sns.jointplot(x=results_10['Distance_d'], y=results_10['buf_er'], kind='scatter', s=0.2).set_axis_labels("Distance displaced (km)", "Error when measured using 10km buffer (seconds)")
p4.ax_marg_y.set_ylim(results['dis_er'].min(), results['dis_er'].max())


fig = plt.figure(figsize=(10,10))
gs = gridspec.GridSpec(2, 2)

mg0 = sfg.SeabornFig2Grid(p1, fig, gs[0])
mg1 = sfg.SeabornFig2Grid(p2, fig, gs[1])
mg2 = sfg.SeabornFig2Grid(p3, fig, gs[2])
mg3 = sfg.SeabornFig2Grid(p4, fig, gs[3])

gs.tight_layout(fig)

plt.savefig('/home/s1891967/diss/Data/Output/resultsgraph.png')


#Calculate medians
print(results['dis_er'].median(), results['near_er']. median(), results['buf_er'].median(), results_10['buf_er'].median())


# Undertake t-tests
a = results['Access'].to_numpy()
b = results['Access_dis'].to_numpy()
c = results['Nearest_ac'].to_numpy()
d = results['within_5_1'].to_numpy()
e = results_10['within_5_1'].to_numpy()

print(f'Displaced: {scipy.stats.ttest_rel(a,b, nan_policy='omit')}')
print(f'Nearest: {scipy.stats.ttest_rel(a,c, nan_policy='omit')}')
print(f'5km buffer: {scipy.stats.ttest_rel(a,d, nan_policy='omit')}')
print(f'10km buffer: {scipy.stats.ttest_rel(a,e, nan_policy='omit')}')







