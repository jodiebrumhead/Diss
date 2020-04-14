import plotly.figure_factory as ff
import pandas as pd
from pandas import read_excel


# find your sheet name at the bottom left of your excel file and assign
# it to my_sheet
my_sheet = 'GanttUpdated'
file_name = 'C:/Users/jodie/Documents/Uni/Diss/GanttUpdated.xlsx' # name of your excel file
df = read_excel(file_name, sheet_name = my_sheet)

print(df)

colors = {'Scoping' : '#e41a1c', 'Literature Review' : '#377eb8', 'Supervisor Input' : '#FFFFFF', 'Research Project '
                                                                                                  'Plan' : '#4daf4a',
          'Analysis' : '#984ea3', 'Final Write-Up' : '#ff7f00', 'Website' : '#ffff33', 'Milestone' : '#000000'}

fig = ff.create_gantt(df, colors=colors, index_col='Group', show_colorbar=True, showgrid_x=True, showgrid_y=True, bar_width=0.5)
fig.update_yaxes(tickfont=dict(size=14))
fig.update_xaxes(tickfont=dict(size=14))

fig.update_layout(
    autosize=False,
    width=1500,
    height=900,
    paper_bgcolor="LightSteelBlue",
    plot_bgcolor="LightSteelBlue"
)
# plot figure
fig.show()

