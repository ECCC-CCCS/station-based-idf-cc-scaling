import xarray as xr
import pandas as pd
import threddsclient
import matplotlib.pyplot as plt
import salem
import numpy as np
import sys
import motionless
from salem import mercator_grid, Map, open_xr_dataset
#np.set_printoptions(threshold=sys.maxsize)
#np.set_printoptions(suppress=True) 


#location of your shapefile
input='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/03 - Data, Code & Models/01 - Data/GIS Layers/'
#input='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/05 - Personal/DeGroot/Support Desk Cases/North Region/'
#output folder
output='C:/Users/degroots/Desktop/Region North/'

region='Northwest Territories / Territoires du Nord-Ouest'
shp = 'gpr_000b11a_e.shp'
#shp='province.shp'

shdf = salem.read_shapefile(input+shp)
shdf = shdf.loc[shdf.PRNAME == region]
print(shdf['min_x'])
print(shdf['min_y'])
print(shdf['max_x'])
print(shdf['max_y'])

# shdf=shdf.set_value(5,'min_x',-141.0)


#List of climate indices 
vars=['tx_max']
rcps=['rcp26','rcp45','rcp85']  
perc = ['p10','p50','p90']
"""
#################################################################################################
#####################################Don't edit anything below!!##########################################
##################################################################################################
"""

portal="https://pavics.ouranos.ca/thredds/catalog/birdhouse/cccs_portal/indices/Final/BCCAQv2/"
selected_var=[]

for var in vars:
    for r in rcps:
        selected_var_a = [ds for ds in threddsclient.crawl(portal+var+"/YS/"+r+'/ensemble_percentiles/'+"catalog.html",depth=10) if '30yAvg' not in ds.name]
        selected_var.append(selected_var_a)
selected_var_flat=[y for x in selected_var for y in x]


table_all=[]
for fld in selected_var_flat:
    r=fld
    r=str(r.opendap_url())
    varN=r.split("/")[-5]
    varNames_1=[]
    rcpN=r.split("/")[-3]
    ds = xr.open_dataset(r)
    lon=ds['lon'].values
    
    ##lon values not pulled
    dsr = ds.salem.subset(shape=shdf, margin=10)
    ##ERROR##
    dsr_ss= dsr.salem.roi(shape=shdf)
    dataSel=dsr_ss
    dataSel.to_netcdf(output+'BCCAQv2_'+'_'+region+'_'+varN+'_'+rcpN+'.nc')
    
# =============================================================================
#     
# ##PLOTTING LON DATA VALUES#######
# x=lon
# y=np.full((1068,),1)
# plt.bar(x,y, width=0.1)
# plt.plot(x,y)
# =============================================================================
        

###PLOTTING LON SHAPEFILE GEOMETRY####


# read the shapefile

# Get the google map which encompasses all geometries
g = salem.GoogleVisibleMap(x=[shdf.min_x.min(), shdf.max_x.max()],
                           y=[shdf.min_y.min(), shdf.max_y.max()],
                           maptype='satellite', scale=2,
                           size_x=400, size_y=400)
ggl_img = g.get_vardata()

# Get each level draining into the lake, then into the last level, and so on
# =============================================================================
# shdf = []
# prev_id = [shdf.iloc[0].MAIN_BAS]
# while True:
#     gd = shdf.loc[shdf.NEXT_DOWN.isin(prev_id)]
#     if len(gd) == 0:
#         break
#     shdf.append(gd)
#     prev_id = gd.HYBAS_ID.unique()
# 
# =============================================================================
# make a map of the same size as the image
sm = salem.Map(g.grid, factor=1)
sm.set_rgb(ggl_img)  # add the background rgb image
# add all the draining basins
cmap = plt.get_cmap('Blues')
for i, gd in enumerate(shdf):
    # here we use a trick. set_shapefile uses PatchCollections internally,
    # which is fast but does not support legend labels.
    # so we use set_geometry instead:
    for g, geo in enumerate(shdf.geometry):
        
        sm.set_geometry(geo, facecolor=cmap,
                        alpha=0.8)

# Get the polygon of the last sink (i.e. the lake) and plot it
#shdf = shdf.loc[shdf.HYBAS_ID == shdf.iloc[0].MAIN_BAS]
#sm.set_shapefile(shdf, linewidth=2)
# Compute the outline of the entire basin and plot it
#shdf = shdf.geometry.unary_union
#sm.set_geometry(shdf['geometry'], linewidth=4)

# plot!
f, ax = plt.subplots(figsize=(18, 12))
ax.set_position([0.05, 0.06, 0.7, 0.9])
sm.visualize(addcbar=False)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.show()

# another method


grid = mercator_grid(center_ll=(-130, 65), extent=(15e5, 15e5))

grid.nx, grid.ny  # size of the input grid

smap = Map(grid, nx=500)

smap.grid.nx, smap.grid.ny  # size of the "image", and thus of the axes

smap.visualize(addcbar=False)

# adding shapefile data:
smap.set_data(shdf['geometry']) 

smap.visualize()




###ANOTHER ATTEMPT####################

# make a local grid from which we will compute the mask
# we make it coarse so that we see the grid points
grid = salem.Grid(proj=salem.wgs84, x0y0=(270, 55), nxny=(250, 75), dxdy=(1, 1))

# read the ocean shapefile (data from http://www.naturalearthdata.com)
oceans = salem.read_shapefile(salem.get_demo_file('ne_50m_ocean.shp'),
                              cached=True)

# read the lake shapefile (data from http://www.naturalearthdata.com)
lakes = salem.read_shapefile(salem.get_demo_file('ne_50m_lakes.shp'),
                              cached=True)

# The default is to keep only the pixels which center is within the polygon:
mask_default = grid.region_of_interest(shape=oceans)
mask_default = grid.region_of_interest(shape=lakes, roi=mask_default)

# But we can also compute a mask from all touched pixels
mask_all_touched = grid.region_of_interest(shape=oceans, all_touched=True)
mask_all_touched = grid.region_of_interest(shape=lakes, all_touched=True,
                                           roi=mask_all_touched)

# Make a map to check our results
sm = salem.Map(grid, countries=False)
sm.set_shapefile(oceans, edgecolor='k', facecolor='none', linewidth=2)
sm.set_shapefile(lakes, edgecolor='k', facecolor='none', linewidth=2)
sm.set_plot_params(cmap='Blues', vmax=2)

# prepare the figure
f, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))

# plot 1
sm.set_data(mask_default)
sm.visualize(ax=ax1, addcbar=False, title='Default')
# plot 2
sm.set_data(mask_all_touched)
sm.visualize(ax=ax2, addcbar=False, title='All touched')

# plot!
plt.tight_layout()
plt.show()