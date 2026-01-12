# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:59:50 2021

Data for CanRCM4 and CanESM2 is found on GPSC or: https://open.canada.ca/data/en/dataset/aa7b6823-fd1e-49ff-a6fb-68076a4a477c

Make a time evolving gif of tas, 1950-2100, using one CanESM2 and CanRCM4 realization.
Can make with absolute temperatures or anomalies (code commented out currently)


@author: VanVlietL
"""
#%% Part 1: Make PlateCarree maps to drape over globe

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.colors as colors
import glob
import numpy as np
import xarray as xr

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

# Get annual average for reanalysis and GCM
flnm = ['C:/Users/vanvlietL/Documents/CanESM2/tas_Amon_CanESM2_historical-r1_r1i1p1_195001-202012.nc',
        'C:/Users/vanvlietL/Documents/CanESM2/tas_Amon_CanESM2_historical-r1_r1i1p1_202101-210012.nc']
tas = xr.open_mfdataset(flnm)
CanESM2 = tas.tas.groupby('time.year').mean().chunk(dict(year=-1))

flnm = glob.glob('C:/Users/vanvlietL/Documents/FWI/CanRCM4/r1i1p1/*')     
tas = xr.open_mfdataset(flnm)
CanRCM4 = tas.tas.groupby('time.year').mean().chunk(dict(year=-1))
cmap = plt.get_cmap('rainbow')

# Anomalies, if desired, uncomment this code
'''
ref = CanESM2.sel(dict(year=slice(1981, 2010))).mean(dim='year')
CanESM2 = CanESM2 - ref
ref = CanRCM4.sel(dict(year=slice(1981, 2010))).mean(dim='year')
CanRCM4 = CanRCM4 - ref
'''

# If desired, to improve visualization, set plotting vmin and vmax to something below 100% 
#     AND only consider latitudes above the equator 
vmax = np.max((CanESM2.sel(lat=slice(0, 90)).quantile(0.98).values,
              CanRCM4.quantile(0.98).values))
vmin = np.min((CanESM2.sel(lat=slice(0, 90)).quantile(0.02).values,
              CanRCM4.quantile(0.02).values))

""" If using anomalies, uncomment this code for colormap
cmap = truncate_colormap(plt.get_cmap('bwr'), 0.5 + vmin/vmax/2, 1)
if abs(vmin) > abs(vmax): cmap = truncate_colormap(plt.get_cmap('bwr'), 0, 0.5 - vmax/vmin/2)
"""

# To create lines for edges of gridcell for CanRCM4, offset rlat and rlon
rlat = CanRCM4.rlat 
rlon = CanRCM4.rlon
rlat_e = np.append(rlat, rlat[-1]+0.44) - 0.22
rlon_e = np.append(rlon, rlon[-1]+0.44) - 0.22

rotated_pole = ccrs.RotatedPole(pole_latitude=42.5, pole_longitude=83) # for CanRCM4 rotated_pole grid

c = 'white'

## Make time-evolving flat images, to drape over spinning globe

for yr in np.arange(1950, 2101):

    pltdataCanESM = CanESM2.sel(year=yr)
    pltdataCanRCM = CanRCM4.sel(year=yr)
    
    fig, axes = plt.subplots(figsize=(20,20), frameon=False)
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.margins(0,0)
    
    # Plot CanESM2 
    ax.pcolormesh(pltdataCanESM.lon, pltdataCanESM.lat, pltdataCanESM, transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax, cmap=cmap, alpha=1, zorder=1) 
    ax.hlines(pltdataCanESM.lat - 1.40625 , 0, 360.25, color=c, linewidth=0.5, zorder=2, transform=ccrs.PlateCarree()) # to 360.25 to show gridline on far right when draped over globe. Offset rlat and rlon to place at edges of gridcells
    ax.vlines(pltdataCanESM.lon + 1.40625, -90, 90, color=c, linewidth=0.5, zorder=2, transform=ccrs.PlateCarree())
    
    # Plot CanRCM4 and gridlines - comment out if you only want time-evolving tas for CanESM2
    ax.pcolormesh(pltdataCanRCM.rlon, pltdataCanRCM.rlat, pltdataCanRCM, transform=rotated_pole, vmin=vmin, vmax=vmax, cmap=cmap, alpha=1, zorder=3)
    ax.hlines(rlat_e, rlon_e[0], rlon_e[-1],  color=c, linewidth=0.2, zorder=4, transform=rotated_pole) 
    ax.vlines(rlon_e, rlat_e[0], rlat_e[-1], color=c, linewidth=0.2, zorder=4, transform=rotated_pole)
    
    # Add default ccrs coastlines, if wanted
    ax.coastlines(linewidth=1, resolution='50m', zorder=5)
    plt.axis('off') # turn off plot axis so it won't appear when draping over globe

    fig.savefig('C:/Users/vanvlietL/Documents/Animations/CanESM2_CanRCM4/flat_anomaly/' + str(yr) + '_' + c + '.jpg', pad_inches=0, bbox_inches="tight")
    plt.close()
    
#%% Method 1, Part 2: Drape over globe and animate with mlab and mpy

import moviepy.editor as mpy
from mayavi import mlab
from tvtk.api import tvtk # python wrappers for the C++ vtk ecosystem

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

dt = 1 # one update = one year of real time
years_per_second = 5 # one second in the video = 5 years in the model
globe = {'yr': 1950, 't': 0}
yts = 50 # years to spin globe fully
dur = 30 # 30*5 = 150 years

def update(globe):
    globe['yr'] = globe['yr'] + dt
    globe['t'] = globe['t'] + dt

def mfig(year):
    try: mlab.close()
    except AttributeError: pass
    image_file = 'C:/Users/vanvlietL/Documents/Animations/CanESM2_CanRCM4/flat_anomaly/' + str(year) + '_white.jpg'     
    auto_sphere(image_file)
    f = mlab.gcf()
    f.scene._lift()
    mlab.view(azimuth=90, elevation=40, distance=4, focalpoint=(0,0,0), roll=None, reset_roll=False, figure=None)
    '''
    # To allow globe to spin, uncomment these lines. May need to adjust rotation speed
    #mlab.process_ui_events()
    #mlab.view(azimuth=360*globe['t']/yts, elevation=40, distance=4, focalpoint=(0,0,0), roll=None, reset_roll=False, figure=None)
    '''
    return mlab.screenshot(antialiased=True)

def make_frame(t):
    """ Return the frame for time t """
    while globe['t'] < years_per_second*t:
        update(globe)
    return mfig(globe['yr'])

animation = mpy.VideoClip(make_frame, duration=dur)
animation.write_videofile('C:/Users/vanvlietL/Documents/Animations/CanESM2_CanRCM4/CanESM2_CanRCM4_white_gridlines_full_anomaly.mp4', fps=years_per_second)
mlab.close() # close final figure

