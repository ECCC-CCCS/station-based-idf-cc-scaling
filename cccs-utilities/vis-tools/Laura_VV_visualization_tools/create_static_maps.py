# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 15:24:49 2021

Create static maps to drape over mayavi globe, for pillow gif methods, or for simpel 3D plot.

This file contains:
    1. Flat (PlateCarree) maps of basic GCM grids (land area fraction): fine and coarse resolution, to use in rotating gifs in 1) above.
    2. Orthographic projection (3D) static maps with matplotlib. To use with pillows gifs in 3) above (not preferred for rotating globes, resolution is not as good, fine for time-evolving non-rotating gifs).
    3. 3D static globes made with mayavi. Input is jpeg of PlateCarree map from 1.
    4. 3D static globe with pyvista. Input is xarray datasets (temperature, land area fraction, etc.)

@author: VanVlietL
"""

#%% 1. Matplotlib lib: flat maps of GCM grids, to drape over globe

'''
Plot static maps of GCM grids, to drape over globe

Having an issue where these plots made with PlateCarree slightly overlap themselves on sides, 
therefore don't fully cover globe when making gif. Instead use Mercator projection, although
it shows up as PlateCarree(?), might be fixed with next cartopy release (0.19)
'''

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import numpy as np

# To allow truncating colormaps to get prefered colours
def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

# Get land area fraction
flnm = 'C:/Users/vanvlietL/Documents/CanESM2/sftlf_fx_CanESM2_historical-r1_r0i0p0.nc'
laf = xr.open_dataset(flnm).squeeze() # land area fraction

# Create an "old" coarse GCM using xarrays coarsen function
old = laf.coarsen(lat=4, coord_func='mean').mean() # coarsen GCM using built-in function
old = old.coarsen(lon=4, coord_func='mean').mean()
old = xr.where(old >= 50, 100, 0) # define land as >= 50% land

cmap = plt.get_cmap('ocean_r') # ocean_r
new_cmap = truncate_colormap(cmap, 0.15, 0.9) # truncate colour map for better colors

# -------- Plot detailed GCM --------

fig, axes = plt.subplots(figsize=(20,20), frameon=False)
ax = plt.axes(projection=ccrs.Mercator())
plt.margins(0,0)

# Plot gridlines separately, in case you want a different colour or linewidth
ax.hlines(laf.lat - 1.40625 , 0, 360, color='white', linewidth=0.5) # Offset horizontal lines by 1.4605 to place lines on edges of gridcells
ax.vlines(laf.lon, -90, 90, color='white', linewidth=0.5) # Don't need to offset here, as we are offsetting longitude before plotting to improve gridlines

# Can set alpha to anything below 1 to add auto gridlines to the images. NB: may no longer work with plt.axis('off')?
iml = ax.pcolormesh(laf.lon + 1.40625, laf.lat, laf.sftlf, shading='nearest', cmap=new_cmap, alpha=0.6) # image land
plt.axis('off') # required to remove border around figure so no lines when draping over globe. Affects how alpha=0.6 works
fig.savefig('C:/Users/vanvlietL/Documents/Animations/detailed_gcm.jpg', bbox_inches='tight', pad_inches=0, dpi=72) # can change DPI or use default 

# -------- Plot coarse GCM --------

fig, axes = plt.subplots(figsize=(20,20), frameon=False)
ax = plt.axes(projection=ccrs.Mercator())
plt.margins(0,0)
ax.hlines(old.lat - 4*1.40625 , 0, 360.25, color='white', linewidth=0.5) # to 360.25 to show gridline on far right when draped over globe
ax.vlines(old.lon + 7.03125, -90, 90, color='white', linewidth=0.5)
iml = ax.pcolormesh(np.arange(5.625, 360, 11.25), old.lat, old.sftlf, shading='nearest', cmap=new_cmap, alpha=0.6) # image land
plt.axis('off') 
fig.savefig('Documents/Animations/coarse_gcm.jpg', bbox_inches='tight',  pad_inches=0, dpi=72) # can change DPI or use default 


#%% 2. Matplotlib Orthographic projection (3D). Not preferred for gifs.
'''
Use matplotlib to map globe using Orthographic projection. Not preferred for gifs.

To use pillow gif method, change view by adjusting latitude as in "for" loop. 
Then turn saved output images into gif as shown here. 
Mayavi method is prefered for showing rotating globe, better resolution and will work better for "coarser" GCM grids
    which might appear segmented with this method.

'''
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
from PIL import Image

flnm = 'C:/Users/vanvlietL/Documents/CanESM2/sftlf_fx_CanESM2_historical-r1_r0i0p0.nc'
flnm2 = 'C:/Users/vanvlietL/Documents/CanESM2/sftof_fx_CanESM2_historical-r1_r0i0p0.nc' # ocean area fraction, not the same as reverse land area fraction
laf = xr.open_dataset(flnm).squeeze()
oaf = xr.open_dataset(flnm2).squeeze()

laf2 = xr.where(laf==0,3, laf)
laf2 = xr.where(laf2 == 100, 0, laf2)
laf2 = laf2.where(laf2 == 3, 100)

# Greats a series of images centre on longitude l1 and latitude 45 (can change in projection info below)
for l1 in np.arange(0,361,10): 
    fig, axes = plt.subplots(figsize=(20,20))
    plt.axis('off')
    cmap = plt.get_cmap('ocean_r') #plt.get_cmap('Blues_r') #'Blues')
    ax = plt.axes(projection=ccrs.Orthographic(l1, 45))
    
    # To plot coloured gridlines, if you don't like the defaults        
    for h in laf2.lon.values:
        ax.plot(np.repeat(h, len(laf2.lat.values) +1) -1.40625 , np.append(laf2.lat.values, 90), transform=ccrs.PlateCarree(), color='white', linewidth=1)
    for h in laf2.lat.values:
        ax.plot(np.append(laf2.lon.values, 360), np.repeat(h, len(laf2.lon.values) +1) + 1.40625, transform=ccrs.PlateCarree(), color='white', linewidth=1)
    
    # Set alpha to anything below 1 to add auto gridlines to the images
    imo = ax.pcolormesh(laf2.lon, laf2.lat, laf2.sftlf, transform=ccrs.PlateCarree(), cmap=plt.get_cmap('Blues_r'), alpha=0.9)  # image ocean
    iml = ax.pcolormesh(laf.lon, laf.lat, laf.sftlf, vmin=0, vmax=100, transform=ccrs.PlateCarree(), cmap=cmap, alpha=0.6) # image land
    
    # Add standard ccrs gridlines for lat-lon
    #gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=2, color='black', alpha=0.8, linestyle='--') # 
    
    fig.savefig('Documents/ani/' + str(l1) + '.png', dpi=100) # can change DPI or use default 
    plt.close()

# Pillow, turns saved images into gif

# filepaths
fp_in = "Documents/ani/"
fp_out = "Documents/ani/pil_image_test.gif"

img, *imgs = [Image.open( fp_in + str(num) + '.png') for num in np.arange(361, 0, 10)]
img.save(fp=fp_out, format='GIF', append_images=imgs, save_all=True, duration=200, bitrate=1000, loop=0)

#%% 3. Mayavi: Drape static (jpg) image over globe

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

image_file = 'C:/Users/vanvlietL/Documents/Animations/world.topo.bathy.jpg'
auto_sphere(image_file)

# This is to prevent the error "ValueError: cannot reshape array of size 16 into shape (0,0,4)" 
f = mlab.gcf()
f.scene._lift()

mlab.view(azimuth=90, elevation=40, distance=None, focalpoint=None, roll=None, reset_roll=True, figure=None)
mlab.savefig('testfile_out.jpg')
mlab.close()
 
#%%%
'''
Create a 3D atmosphere, overlaid on top of a globe with a surface field using pyvista.
Can plot any xarray DataArrays using method below

Resources for code below: 
    - https://docs.pyvista.org/examples/02-plot/spherical.html
    - https://github.com/dennissergeev/exoconvection-apj-2020/blob/master/code/Fig01-Model-Set-Up-3D.ipynb
    - https://docs.pyvista.org/examples/02-plot/orbit.html#sphx-glr-examples-02-plot-orbit-py
    - https://docs.pyvista.org/examples/01-filter/compute-normals.html#sphx-glr-examples-01-filter-compute-normals-py
'''

import pyvista as pv
import numpy as np
import xarray as xr

pv.set_plot_theme("document") # background = white

def _cell_bounds(points, bound_position=0.5):
    """
    Calculate coordinate cell boundaries.

    Parameters
    ----------
    points: numpy.array
        One-dimensional array of uniformly spaced values of shape (M,)
    bound_position: bool, optional
        The desired position of the bounds relative to the position
        of the points.

    Returns
    -------
    bounds: numpy.array
        Array of shape (M+1,)

    Examples
    --------
    >>> a = np.arange(-1, 2.5, 0.5)
    >>> a
    array([-1. , -0.5,  0. ,  0.5,  1. ,  1.5,  2. ])
    >>> cell_bounds(a)
    array([-1.25, -0.75, -0.25,  0.25,  0.75,  1.25,  1.75,  2.25])
    """
    assert points.ndim == 1, "Only 1D points are allowed"
    diffs = np.diff(points)
    delta = diffs[0] * bound_position
    bounds = np.concatenate([[points[0] - delta], points + delta])
    return bounds

flnm = 'C:/Users/vanvlietL/Documents/CanESM2/sftlf_fx_CanESM2_historical-r1_r0i0p0.nc'
laf = xr.open_dataset(flnm).sel(lon=slice(0, 270)).squeeze() # land area
laf_full = xr.open_dataset(flnm).squeeze() # land area

RADIUS = 1.0

# Grid for atmospheric levels 
xx_bounds = _cell_bounds(laf.lon.values)
yy_bounds = _cell_bounds(90 - laf.lat.values) # grid_from_sph_coords() expects polar angle
levels = RADIUS * np.arange(1.01, 1.5, 0.08)
grid_scalar = pv.grid_from_sph_coords(xx_bounds, yy_bounds, levels)
grid_scalar.cell_arrays["zlevs"] = np.array(np.tile(laf.sftlf.values, levels.size - 1)).swapaxes(-2, -1).ravel("C")

# wireframe version of atmosphere -- each layer (i.e. surface vs atosphere above)
# must be at a different 'height' (level) to show in plotter, need a separate dataframe
levels = RADIUS * np.arange(1.02, 1.5, 0.08)
wire_scalar = pv.grid_from_sph_coords(xx_bounds, yy_bounds, levels)
wire_scalar.cell_arrays["zlevs"] = np.array(np.tile(laf.sftlf.values, levels.size - 1)).swapaxes(-2, -1).ravel("C")

# Grid for surface
xx_bounds = _cell_bounds(laf_full.lon.values)
yy_bounds = _cell_bounds(90 - laf_full.lat.values) # grid_from_sph_coords() expects polar angle

levels = [RADIUS * 1.01]
grid_sfc = pv.grid_from_sph_coords(xx_bounds, yy_bounds, levels)
grid_sfc.cell_arrays["laf"] = np.array(laf_full.sftlf.values).swapaxes(-2, -1).ravel("C")

# Wireframe version of surface 
levels = [RADIUS * 1.02]
wire_sfc = pv.grid_from_sph_coords(xx_bounds, yy_bounds, levels)
wire_sfc.cell_arrays["laf"] = np.array(laf_full.sftlf.values).swapaxes(-2, -1).ravel("C")

# Make a plot
p = pv.Plotter()
p.add_mesh(pv.Sphere(radius=RADIUS))

# Global surface 
p.add_mesh(grid_sfc, clim=[0.1, 2.0], cmap="ocean_r", show_scalar_bar=False)# smooth_shading=False
p.add_mesh(wire_sfc, clim=[0.1, 2.0], color="b", style='wireframe', opacity=0.2) 

# Atmospheric grid
p.add_mesh(wire_scalar, clim=[0.1, 2.0], opacity=0.2, color="white", style='wireframe') # cmap="plasma"
#p.add_mesh(grid_scalar, clim=[0.1, 2.0], opacity=0.2, color="grey")

p.show(auto_close=False) # close with q on keyboard and then gif will generate (next part of code)

# To save image, set up view and save screen shot
imgname = 'imgname.jpg'
flon, flat = 270, 40 # focus 
p.set_position(pv.grid_from_sph_coords(flon, [90 - flat], [8*RADIUS]).points)  # default: [(5.485199280057733, 5.485199280057733, 5.485199280057733),
p.set_focus((0, 0, 0))
p.set_viewup((0, 1, 0)) # default: 0, 0 ,1

p.show(screenshot=imgname, auto_close=False) # to save jpeg of image view

               

