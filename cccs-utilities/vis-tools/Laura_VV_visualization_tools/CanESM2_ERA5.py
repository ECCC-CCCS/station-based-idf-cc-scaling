# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 11:36:55 2021

ERA5 data was downloaded from: https://climexp.knmi.nl/selectfield_rea.cgi?id=someone@somewhere
CanESM2 data can be downloaded from https://open.canada.ca/data/en/dataset/aa7b6823-fd1e-49ff-a6fb-68076a4a477c

Make maps of tas for 1980-2010 for CAnESM2 and ERA5. Regrid ERA5 to CanESM2 grid first.

File contains:
    1. Code to regrid - I don't think it can be done on Windows (use linux)
    2. Create globes with a variety of color schemes to test

@author: VanVlietL
"""

#%% 1. Regrid ERA5 to same grid as CanESM2. Can only
# Code to regrid ERA5 to same grid as CanESM2 for better comparison.
# I believe xesmf only works on linux environment, cannot be run on Windows.

import xarray as xr
import xesmf as xe

prescript = '/***REMOVED***/***REMOVED***/'

rg_in = xr.open_dataset(prescript + 'ERA5_tas.nc')['mean']
rg_ot = xr.open_dataset(prescript + 'CanESM2_tas.nc').tas

ds_out = xr.Dataset({'lat': (['lat'], rg_ot.lat),  'lon': (['lon'], rg_ot.lon)})

regridder = xe.Regridder(rg_in, ds_out, 'bilinear')

out = regridder(rg_in)
    
out.to_netcdf(prescript + 'regridded_ERA5_1980_2009.nc') # 

#%% 2. Create map of CanESM2 and ERA5

import numpy as np
import xarray as xr
from scipy import stats
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cmcrameri import cm
import seaborn as sns
import pandas as pd
from mayavi import mlab
from tvtk.api import tvtk # python wrappers for the C++ vtk ecosystem

# Load data, take annual average for reanalysis and GCM
dct = {}

flnm = 'C:/Users/vanvlietL/Documents/CanESM2/tas_Amon_CanESM2_historical-r1_r1i1p1_195001-202012.nc'
GCM_tas = xr.open_dataset(flnm).sel(time = slice('1980-01-01', '2009-12-31'))

flnm = 'C:/Users/vanvlietL/Documents/Reanalysis/m1113.nc' # 1980-2010 as per https://climexp.knmi.nl/getmomentsfield.cgi              
re_tas = xr.open_dataset(flnm, decode_times=False ).squeeze()
                                                              
dct['CanESM2_tas'] = GCM_tas.tas.mean(dim='time')
dct['ERA5_tas'] = re_tas['mean'].mean(dim='time') # just for comparison purposes
dct['ERA5_tas_regridded'] = xr.open_dataset('C:/Users/vanvlietL/Documents/Animations/GCM_reanalysis/regridded_ERA5_1980_2009.nc')['mean']

# Get a standardized vmax and vmin for comparison
df = pd.DataFrame(columns=dct.keys(), index=['vmin','vmax'])
for key, pltdata in dct.items():
    try:
        dat = pltdata.sel(lat=slice(90,0))
        df.loc['vmin', key] = dat.min().values
        df.loc['vmax', key] = dat.max().values
    except ValueError: 
        dat = pltdata.sel(lat=slice(0,90))
        df.loc['vmin', key] = dat.min().values
        df.loc['vmax', key] = dat.max().values
df.CanESM2_tas = df.CanESM2_tas - 273.15

# From df, get min and max
vmin = -30.7
vmax = 34.3

cmaps = ['cet_linear_kryw_5_100_c67_r', 'cmo.thermal', 'cmo.solar_r', 'rocket', 
         cm.turku, cm.vik, cm.lajolla, cm.batlow, cm.roma_r, cm.lapaz]
names = ['cet_linear_kryw_5_100_c67_r', 'cmo.thermal',  'cmo.solar_r', 'rocket', 
         'turku', 'vik', 'lajolla', 'batlow', 'roma_r', 'lapaz']
cmaps = ['Spectral_r', 'turbo', 'bwr', 'jet', 'rainbow', cm.vik, cm.lajolla, cm.batlow, cm.roma_r]
names = ['Spectral_r', 'turbo', 'bwr', 'jet', 'rainbow', 'vik', 'lajolla', 'batlow', 'roma_r']

# Plot flat, PlateCarree, images with variety of color maps 
for key, pltdata in dct.items():

   if key == 'CanESM2_tas':
        pltdata = pltdata - 273.15

   for cmp, name in zip(cmaps, names):
    
        try: cmap=plt.get_cmap(cmp)
        except ValueError:
            cmap=sns.color_palette(cmp, as_cmap=True)
        except TypeError:   cmap = cmp
    
        for alph in [1, 0.4]:         
            fig, axes = plt.subplots(figsize=(20,20), frameon=False)
            ax = plt.axes(projection=ccrs.PlateCarree())
            plt.margins(0,0)
            #ax.hlines(ff.lat - 4*1.40625 , 0, 360.25, color='white', linewidth=0.5) # to 360.25 to show gridline on far right when draped over globe
            #ax.vlines(ff.lon + 7.03125, -90, 90, color='white', linewidth=0.5)
           # ax.pcolormesh(pltdata.lon, pltdata.lat, pltdata, shading='nearest', transform=ccrs.PlateCarree(), cmap=cmap, alpha=alph) # image land
            ax.pcolormesh(pltdata.lon, pltdata.lat, pltdata, transform=ccrs.PlateCarree(), cmap=cmap, vmin=vmin, vmax=vmax, alpha=alph) # image land
            ax.coastlines(linewidth=1, resolution='50m')
            plt.axis('off') 
               
            fig.savefig('C:/Users/vanvlietL/Documents/Animations/GCM_reanalysis/' + key + '_' + name + '_' + str(alph) + '.jpg', pad_inches=0, bbox_inches="tight")

# Drape over globe and save
def auto_sphere(image_file):
    # create a figure window (and scene)
    fig = mlab.figure(size=(600, 600), bgcolor=(1,1,1)) # set background colour to white

    # load and map the texture
    img = tvtk.JPEGReader()
    img.file_name = image_file
    texture = tvtk.Texture(input_connection=img.output_port, interpolate=1)
    # (interpolate for a less raster appearance when zoomed in)

    # use a TexturedSphereSource, a.k.a. getting our hands dirty
    R = 1
    Nrad = 180

    # create the sphere source with a given radius and angular resolution
    sphere = tvtk.TexturedSphereSource(radius=R, theta_resolution=Nrad,
                                       phi_resolution=Nrad)

    # assemble rest of the pipeline, assign texture    
    sphere_mapper = tvtk.PolyDataMapper(input_connection=sphere.output_port)
    sphere_actor = tvtk.Actor(mapper=sphere_mapper, texture=texture)
    fig.scene.add_actor(sphere_actor)

for key in ['CanESM2_tas', 'ERA5_tas', 'ERA5_tas_regridded']:
    for name in names:
        image_file = 'C:/Users/vanvlietL/Documents/Animations/GCM_reanalysis/' + key + '_' + name + '_1.jpg'
        auto_sphere(image_file)
    
        # This is to prevent the error "ValueError: cannot reshape array of size 16 into shape (0,0,4)" 
        f = mlab.gcf()
        f.scene._lift()
        
        mlab.view(azimuth=90, elevation=40, distance=None, focalpoint=None, roll=None, reset_roll=True, figure=None)
        mlab.savefig('C:/Users/vanvlietL/Documents/Animations/GCM_reanalysis/globe_' + key + '_'  + name + '.jpg')
        #mlab.screenshot(antialiased=True)
        mlab.close()
