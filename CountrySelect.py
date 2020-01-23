"""Import excel spreadsheets of Health and DHS data and cross reference to identify possible countries"""

from pandas import read_excel
from openpyxl import Workbook

# find your sheet name at the bottom left of your excel file and assign
# it to my_sheet
my_sheet = 'SSA MFL'
file_name = 'C:/Users/jodie/Documents/Uni/Diss/Health.xlsx' # name of your excel file
healthdf = read_excel(file_name, sheet_name = my_sheet)
healthls = healthdf['Country'].unique()

my_sheet = 'Sheet1'
file_name = 'C:/Users/jodie/Documents/Uni/Diss/DHSgeo.xlsx' # name of your excel file
dhsdf = read_excel(file_name, sheet_name = my_sheet)


dhsdf = dhsdf[dhsdf['GPS Datasets'] == 'Data Available']

# new data frame with split value columns
new = dhsdf["Country/Year"].str.split(" ", n=1, expand=True)

# making separate first name column from new data frame
dhsdf["Country"] = new[0]

# making separate last name column from new data frame
dhsdf["Year"] = new[1]

# Dropping old Name columns
dhsdf.drop(columns=["Country/Year"], inplace=True)

dhsdf = dhsdf[dhsdf['Country'].isin(healthls)]

dhsdf['freq'] = dhsdf.groupby('Country')['Country'].transform('count')

potentials = dhsdf[dhsdf['freq'] > 2]  # change to greater than 3

cols = ['Country', 'Year', 'freq', 'Type', 'Status', 'Phase', 'Recode', 'Dates of Fieldwork', 'Final Report', 'Survey Datasets', 'GPS Datasets', 'HIV/Other', 'SPA Datasets']
#reorder columns??

potentials = potentials[cols]

print(potentials['Country'].unique())

potentials.to_excel("C:/Users/jodie/Documents/Uni/Diss/Potential.xlsx")


