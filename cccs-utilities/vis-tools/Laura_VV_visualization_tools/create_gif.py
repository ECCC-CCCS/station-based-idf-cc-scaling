# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 14:58:31 2021

This file contains 4 methods for rotating/time-evolving globe gif creation:

    Method 1: Static rotating image (globe) with mayavi. Input: jpeg image which is then "draped" over globe. Requires: mayavi, tvtk.api, moviepy.editor
    Method 2: Static rotating image with pyvista. Input: xarray files. Requires pyvista.
    Method 3: Pillow or Imageio gif. From any any set of images. Requires Pillow or Imageio.
    Method 4: Time-evolving and rotating gif with mayavi. Requires: mayavi, tvtk.api, moviepy.editor

@author: VanVlietL
"""

#%% Method 1: Using mayavi, create a globe and drape any image over it with mayavi, convert to gif or movie with mpy

'''
Create a globe and drape any image over it with mayavi, convert to gif or movie with mpy
Great for static image/globes you just want to turn into a gif. Will require some tweaking to use for "change over time" (and may be easier to use matplotlib method)

Note: Create a new environment to download mayavi to avoid conflicts
Note: Potentially could do this better with pyvista (see 3D_atmosphere code) vs mayavi 
Both mayavi and pyvista are wrappers for  (as far as I understand) which allows for great 3D plotting and gif making
pyvista is super useful for 3D meshgrids such as GCMs, seems less likely to break, and more user-friendly / intuitive

For static version see create_static_map.py file.

Sources:
     - Drape image on globe: https://stackoverflow.com/questions/53074908/map-an-image-onto-a-sphere-and-plot-3d-trajectories
     - Create gif: http://zulko.github.io/blog/2014/11/29/data-animations-with-python-and-moviepy/ 
'''

from mayavi import mlab
from tvtk.api import tvtk # python wrappers for the C++ vtk ecosystem
import moviepy.editor as mpy

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

#  Blue marble collection: https://visibleearth.nasa.gov/collection/1484/blue-marble?page=5
image_file = 'Documents/Animations/coarse_gcm.jpg'
auto_sphere(image_file)
#mlab.show()

# This is to prevent the error "ValueError: cannot reshape array of size 16 into shape (0,0,4)" 
f = mlab.gcf()
f.scene._lift()

duration = 6 # duration of gif

def make_frame(t):
    mlab.process_ui_events()
    mlab.view(azimuth = 360*t/duration, distance=6) # distance is distance of "camera" from globe. 
    return mlab.screenshot(antialiased=True)

animation = mpy.VideoClip(make_frame, duration=duration)
animation.write_videofile("Documents/Animations/coarse_gcm.mp4", fps=25) # Update frames per second as desired
#animation.write_gif("Documents/Animations/coarse_gcm.gif", fps=25) # GIF generation takes longer, and makes much larger file
mlab.close()

#%% Method 2: pyvista
"""
Create a 3D atmosphere, overlaid on top of a globe with a surface field using pyvista.
Can plot any xarray DataArrays using methods below

Resources for code below: 
    - https://docs.pyvista.org/examples/02-plot/spherical.html
    - https://github.com/dennissergeev/exoconvection-apj-2020/blob/master/code/Fig01-Model-Set-Up-3D.ipynb
    - https://docs.pyvista.org/examples/02-plot/orbit.html#sphx-glr-examples-02-plot-orbit-py
    - https://docs.pyvista.org/examples/01-filter/compute-normals.html#sphx-glr-examples-01-filter-compute-normals-py
"""

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

# For gif, open movie and rotated view around globe
filename = 'C:/Users/vanvlietL/Documents/Animations/GCM_wiremesh.mp4'
filename = 'C:/Users/vanvlietL/Documents/Animations/test.mp4'
p.open_movie(filename, framerate=24) # movie is smaller than gif 
#p.open_gif(filename)

path = p.generate_orbital_path(n_points=360, viewup=[0, 0, 1], shift=6) # viewup controls orbital plane, shift controls view
p.orbit_on_path(path, write_frames=True) #focus=None, step=0.5 --> camera focus, timestep 
p.close()


#%% Method 3: Use pillow or imageio to create a gif with a number of saved iamge files
'''
Pillow method: Turn saved images into gif
To create images of a globe see "create_static_maps.py" file

Source: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
'''
import numpy as np
from PIL import Image
import glob
import imageio

# filepaths
fp_in = "Documents/ani/"
fp_out = "Documents/ani/pil_image_test.gif"

img, *imgs = [Image.open( fp_in + str(num) + '.png') for num in np.arange(361, 0, 10)]
img.save(fp=fp_out, format='GIF', append_images=imgs, save_all=True, duration=200, bitrate=1000, loop=0)

'''
Imagio method: Turn saved images info gif
I prefer pillow

'''    
fp_in = "Documents/ani/"
images = []
for num in np.arange(0,361,10): 
    filename = fp_in + str(num) + '.png'
    images.append(imageio.imread(filename))
imageio.mimsave('Documents/ani/image.gif', images, fps=10)

#For longer movies, use the streaming approach:

import imageio
with imageio.get_writer('Documents/ani/movie.gif', mode='I') as writer:
    for filename in  sorted(glob.glob(fp_in)):
        image = imageio.imread(filename)
        writer.append_data(image)
        
#%% Method 4: Mayavi time-evolving and/or rotating gif
        
''' 
Mayavi time-evolving and/or rotating gif
For an example with CanESM2_CaRCM4, see CanESM2_CanRCM4_tas_1950_2100.py

'''

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

dur = 5 # 30 * 5 = 150 years

def update(globe):
    globe['yr'] = globe['yr'] + dt
    globe['t'] = globe['t'] + dt

def mfig(year):
    try: mlab.close()
    except AttributeError: pass
    image_file = 'C:/Users/vanvlietL/Documents/Animations/CanESM2_CanRCM4/flat/' + str(year) + '_white.jpg'     
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
animation.write_videofile('C:/Users/vanvlietL/Documents/Animations/CanESM2_CanRCM4/CanESM2_CanRCM4_white_gridlines_full.mp4', fps=years_per_second)
mlab.close() # close final figure

