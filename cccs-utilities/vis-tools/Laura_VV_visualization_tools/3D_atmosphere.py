# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 15:17:18 2021

@author: VanVlietL

Create a 3D atmosphere, overlaid on top of a globe with a surface field using pyvista.

Need to select rotating gif or static image output and uncomment appropriate code at bottom.

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

'''
# For gif, open movie and rotated view around globe
filename = 'C:/Users/vanvlietL/Documents/Animations/GCM_wiremesh.mp4'
filename = 'C:/Users/vanvlietL/Documents/Animations/test.mp4'
p.open_movie(filename, framerate=24) # movie is smaller than gif 
#p.open_gif(filename)

path = p.generate_orbital_path(n_points=360, viewup=[0, 0, 1], shift=6) # viewup controls orbital plane, shift controls view
p.orbit_on_path(path, write_frames=True) #focus=None, step=0.5 --> camera focus, timestep 
p.close()
'''
'''
# To save image, set up view and save screen shot
imgname = 'imgname.jpg'
flon, flat = 270, 40 # focus 
p.set_position(pv.grid_from_sph_coords(flon, [90 - flat], [8*RADIUS]).points)  # default: [(5.485199280057733, 5.485199280057733, 5.485199280057733),
p.set_focus((0, 0, 0))
p.set_viewup((0, 1, 0)) # default: 0, 0 ,1

p.show(screenshot=imgname, auto_close=False) # to save jpeg of image view

'''