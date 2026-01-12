# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 14:59:50 2021

Data for CanRCM4 and CanESM2 is found on GPSC or: https://open.canada.ca/data/en/dataset/aa7b6823-fd1e-49ff-a6fb-68076a4a477c

Make a time evolving gif of tas, 1950-2100, using one CanESM2 realization.
Can make with absolute temperatures or anomalies (code commented out currently).

I've attemped to add a title (year) to the gif without success, incomplete code commented out below 

@author: VanVlietL
"""
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
from PIL import Image
import matplotlib.colors as colors

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

# Get annual average for reanalysis and GCM

flnm = ['C:/Users/vanvlietL/Documents/CanESM2/tas_Amon_CanESM2_historical-r1_r1i1p1_195001-202012.nc',
        'C:/Users/vanvlietL/Documents/CanESM2/tas_Amon_CanESM2_historical-r1_r1i1p1_202101-210012.nc']
       
tas = xr.open_mfdataset(flnm).chunk(dict(time=-1))
tas_y = tas.tas.groupby('time.year').mean()

ref = tas_y.sel(dict(year=slice(1981, 2010))).mean(dim='year')
tas_y = tas_y - ref

vmax = tas_y.sel(lat=slice(0, 90)).max().values
vmin = tas_y.sel(lat=slice(0, 90)).min().values

cmap = truncate_colormap(plt.get_cmap('bwr'), 0.5 + vmin/vmax/2, 1)
if abs(vmin) > abs(vmax): cmap = truncate_colormap(plt.get_cmap('bwr'), 0, 0.5 - vmax/vmin/2)

for yr in np.arange(1950, 2101):
    
    pltdata = tas_y.sel(year=yr)
    
    fig, axes = plt.subplots(figsize=(20,20), frameon=False)
    ax = plt.axes(projection=ccrs.PlateCarree())
    plt.margins(0,0)
    #ax.hlines(ff.lat - 4*1.40625 , 0, 360.25, color='white', linewidth=0.5) # to 360.25 to show gridline on far right when draped over globe
    #ax.vlines(ff.lon + 7.03125, -90, 90, color='white', linewidth=0.5)
   # ax.pcolormesh(pltdata.lon, pltdata.lat, pltdata, shading='nearest', transform=ccrs.PlateCarree(), cmap=cmap, alpha=alph) # image land
    ax.pcolormesh(pltdata.lon, pltdata.lat, pltdata, transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax, cmap=cmap, alpha=1) # image land
    ax.coastlines(linewidth=1, resolution='50m')
    plt.axis('off') 
       
    fig.savefig('C:/Users/vanvlietL/Documents/Animations/CanESM2_tas_1950_2100/flat_anomaly/' + str(yr) + '.jpg', pad_inches=0, bbox_inches="tight")
    plt.close()

#%%
import moviepy.editor as mpy
from mayavi import mlab
from tvtk.api import tvtk # python wrappers for the C++ vtk ecosystem
import  moviepy.editor as mpy
import numpy as np

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

dt = 1.0 # one update = one year of real time
years_per_second = 5 # one second in the video = 5 years in the model
globe = {'yr': 1950, 't':0}

def update(globe):
    globe['yr'] = globe['yr'] + 1
    globe['t'] = globe['t'] + 1
   # image_file = 'C:/Users/vanvlietL/Documents/Animations/CanESM2_tas_1950_2100/flat/' + str(globe['yr']) + '.jpg'

def mfig(year):
    try: mlab.close()    # clear any figures
    except AttributeError: pass
    image_file = 'C:/Users/vanvlietL/Documents/Animations/CanESM2_tas_1950_2100/flat_anomaly/' + str(year) + '.jpg'     
    auto_sphere(image_file)
    f = mlab.gcf()
    f.scene._lift()
    mlab.view(azimuth=90, elevation=40, distance=4, focalpoint=(0,0,0), roll=None, reset_roll=False, figure=None)
    return mlab.screenshot(antialiased=True)

def make_frame(t):
    """ Return the frame for time t """
    while globe['t'] < years_per_second*t:
        update(globe)
    return mfig(globe['yr'])

def apply_title(t):
    """ Returns a clip with the effect applied and a top label"""    
    txt = (mpy.TextClip(str(globe['yr']), font="Amiri-Bold", fontsize=25,
                        bg_color='white', size=(600,600))
           .set_position(("center")))
    return txt

animation = mpy.VideoClip(make_frame, duration=30)
animation.write_videofile('C:/Users/vanvlietL/Documents/Animations/CanESM2_tas_1950_2100/CanESM2_tas_anomaly_1950_2100.mp4', fps=years_per_second)
mlab.close() # close final figure

#title = mpy.VideoClip(apply_title, duration=30)
#ani_out = mpy.concatenate_videoclips([txt, animation])
#ani_out.write_videofile('C:/Users/vanvlietL/Documents/Animations/CanESM2_tas_1950_2100/test_title.mp4', fps=5)

#animation.write_gif("test.gif", fps=20)
#final = mpy.CompositeVideoClip([make_frame,apply_title], duration=30)


