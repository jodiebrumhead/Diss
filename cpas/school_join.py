import pandas as pd
import geopandas as gpd
import numpy as np
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

# Read in both data sources as dataframes
gov = pd.read_csv('C:/Users/jodie/Documents/Gary Unicef Stuff/gov_schools.csv', header='infer', index_col=0)
osm = pd.read_csv('C:/Users/jodie/Downloads/Schools_classifying_append.csv', header='infer', index_col=0)

# change P.S to PRIMARY SCHOOL in government schools list for better matching
osm['name'] = osm['name'].replace({'Primary School' : 'P.S'}, regex=True)
gov['School'] = gov['School'].replace({'P.7 SCHOOL' : 'P.S'}, regex=True)
gov['County'] = gov['County'].replace({'M/C' : 'Municipality'}, regex=True)
gov['County'] = gov['County'].replace({'MC' : 'Municipality'}, regex=True)
osm['addr_conam'] = osm['addr_conam'].replace({' County' : ''}, regex=True)

# Concatenate to make 'address' ... maybe change something here...
gov['address'] = gov['School'] + ' ' + gov['Parish'] + ' ' + gov['County'] + ' ' + gov['District']

osm = osm.fillna('') # otherwise does not concatenate where nan

osm['address'] = osm['name'] + ' ' + osm['addr_pname'] + ' ' + osm['addr_conam'] + ' ' + osm['addr_dname']

osm = osm.head(50)

print(osm)

# find best match from OSM schools for Government schools using fuzzy matching and create new dataframe of this
lst = []

osm['gov_match'], osm['score'], osm['gov_index'] = np.NaN, np.NaN, np.NaN


for index, row in osm.iterrows():
    osm.loc[index,'gov_match'], osm.loc[index,'score'], osm.loc[index,'gov_index'] = process.extractOne(row['address'], gov['address'], scorer=fuzz.token_sort_ratio)

print(osm)


# Group were best match is the same.. (i.e. find duplicates) and then find the maximum value (i.e. best match)
grouped = osm.groupby('gov_index')
df1 = grouped['score'].max().rename('mx')
df2 = osm.merge(df1, left_on = 'gov_index', right_index=True)


# where duplicate values and not best match then make NaN as no match
df2.loc[df2['score'] != df2['mx'], ['gov_index']] = np.NaN
# remove where score low indicating not a good match
df2.loc[df2['score'] < 70, ['gov_index']] = np.NaN


df2['government_ps'] = [True if x == x else False for x in df2['gov_index']]

df2.to_csv('C:/Users/jodie/Documents/Gary Unicef Stuff/osm2.csv')

print(df2)

# count where no match
count_nan = len(df2[3]) - df2[3].count()
print(count_nan)


# TODO: join OSM df back to the shapefile so they are spatially referenced... using OSM ID

osm_shp = gpd.read_file('')

osm_shp = osm_shp.merge(osm, how='inner', on='osm_id')

print(osm_shp)

osm_shp.to_file('')



