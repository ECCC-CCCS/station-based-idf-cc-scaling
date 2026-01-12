import pandas as pd
import xarray as xr
import numpy as np
import threddsclient
from bokeh.io import show
from bokeh.io import export_png
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure
from bokeh.models import Range1d
import time
import matplotlib.pyplot as plt

start = time.time()

latitude=49.4928
longitude=-117.2948


vars= ['tx_min','tx_mean','tx_max','tn_min','tn_mean','tn_max','tg_mean']

portal= 'https://pavics.ouranos.ca/thredds/catalog/birdhouse/cccs_portal/indices/Final/ANUSPLIN_v1/'

output='C:/Users/degroots/Temporary Files/Data/Outputs/threddsserver outputs/'

selected_var = []


for var in vars:
    selected_var_a=[ds for ds in threddsclient.crawl(portal + var + "/YS/" + "catalog.html", depth=10)] #if "nrcan" in ds.name]
    
    selected_var.append(selected_var_a)

selected_var_flat=[y for x in selected_var for y in x]
n=len(selected_var_flat)    
table_all= []

for n in range (0,n):
    r=selected_var_flat[n]
    r= str(r.opendap_url())
    varN=r.split("/")[-3]
    ds= xr.open_dataset(r)
    dataSel= ds[varN].sel(lat=latitude, lon=longitude, method='nearest')
    t=pd.to_datetime(dataSel.time.values)
    timestring = pd.Series(t.strftime('%Y-%m-%d'))
    YYstring = pd.Series(t.strftime('%Y'))
    MMstring = pd.Series(t.strftime('%m'))
    DDstring = pd.Series(t.strftime('%d'))
    values=pd.Series(dataSel.values)
    table = pd.concat([timestring, YYstring, MMstring, DDstring, values], axis=1)
    table.columns=['date', 'year', 'month', 'day', varN]
    table = table.melt(id_vars = ['date','day','month','year'])
    #table=(table['value'] - 273.15)
    plt.figure()
    plt.plot(table['date'][n] ,table['value'][n])
    table_all.append(table)
#    table_all=table_all['variable'] - 273.15)
    frame=pd.concat(table_all)
      
      
    frame_all=frame
    frame_all=frame_all.drop(['day','month'], axis=1)
    frame_all=frame_all.set_index('date')
    frame_all=(frame_all['value'] - 273.15)
    frame_all= pd.DataFrame(frame_all)
#frame_all.to_csv(output+'ANUPSLIN_v1_annual.csv')


# bokeh plotting

#for varN in frame_all:
    
#1) get/prepare data- see above
    dates=np.array(frame_all.index,dtype=np.datetime64)
#dates2= np.unique(dates)
    source= ColumnDataSource(data=dict(date=dates, close=frame_all['value']))


#2) output_file() for exporting plot- # do this at the START- # do not know if this is required- leave out for now


#3) create figure object

    p = figure(title=varN+ '-' + '1950-2013',plot_height=300, plot_width=800, tools="xpan", toolbar_location=None,
           x_axis_type="datetime", x_axis_location="above",
           background_fill_color="#efefef", x_range=(dates[-27], dates[-1])) #y_range=Range1d(-25, 20))


    
# ALL of figure (plot) objects are passed directly into figure()
#4) add features to plot- ie renderers
    p.line('date', 'close', source=source)
    p.title.text_font_size = '15pt'
    p.y_range=Range1d(-30, 22)
    #p.xanchor='center'

#5) also: adding ATTRIBUTES directly to the figure is common
    p.yaxis.axis_label = 'Temperature (C)'
       
    # creating SECOND figure now   
    select = figure(title="Drag the middle and edges of the selection box to change the range above",
                plot_height=130,x_range=(dates[0], dates[-1]), plot_width=800, y_range=p.y_range,
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef")

    
    # now for bokeh.models small changes
    
    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    
    # now for adding renderers and attributes directly to the SECOND figure
    
    
    select.line('date', 'close', source=source)
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool


    plot= show(column(p, select))
    #export_png(plot, filename= varN +'plot.png')

print('It took', time.time()-start, 'seconds.')
