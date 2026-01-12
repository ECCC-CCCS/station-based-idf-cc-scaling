# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:09:29 2021

Two parts to this file:
    - first to extract data from kml file (can download modelling centres as kml from 
                                         https://pcmdi.llnl.gov/CMIP6/ map at bottom)
    - second to take this csv (also on github) and convert to globe with pyvista,
        which can then be animated or saved as static image
        Note that I haven't figured out how to add labels to this. Also might be better 
        to plot as points over another image (e.g. temperature)
        
Note: Needs to close pyvista IDE with q on keyboard before gif will generate, or to
"close" on console so that you can continue trialling code

@author: VanVlietL
"""

#%% Extract data from kml file, downloaded from map available on CMIP6 website homepage

from fastkml import kml, geometry 
import pandas as pd
import numpy as np

with open("C:/Users/vanvlietL/Documents/Animations/ModellingCentres/CMIP6ESGF contributors.kml", 'rt', encoding="utf-8") as myfile:
    doc=myfile.read()


k = kml.KML() # create fastkml object
k.from_string(doc.encode('utf-8')) # read doc string
document = list(k.features())

features = list(k.features())

features[0].features()
f2 = list(features[0].features())
f3 = list(f2[2].features())

df = pd.DataFrame(columns=['name', 'lat', 'lon', 'z', 'description'], index=np.arange(0, len(f3)))

for feat, i in zip(f3, range(0, len(f3))):
    df.loc[i, 'name'] = feat.name
    df.loc[i, 'description'] = feat.description
    df.loc[i, 'lon'] = feat.geometry.x
    df.loc[i, 'lat'] = feat.geometry.y
    df.loc[i, 'z'] = feat.geometry.z
    
df.to_csv("C:/Users/vanvlietL/Documents/Animations/ModellingCentres/model_centres.csv")

#%%

import pandas as pd
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

# Get land area fraction for basemap
flnm = 'C:/Users/vanvlietL/Documents/CanESM2/sftlf_fx_CanESM2_historical-r1_r0i0p0.nc'
laf = xr.open_dataset(flnm).squeeze() # land area

# Get data on modelling  centres
df = pd.read_csv("C:/Users/vanvlietL/Documents/Animations/ModellingCentres/model_centres.csv", index_col="Unnamed: 0")

RADIUS = 1.0

# Grid for surface
xx_bounds = _cell_bounds(laf.lon.values)
yy_bounds = _cell_bounds(90 - laf.lat.values) # grid_from_sph_coords() expects polar angle

levels = [RADIUS * 1.01]
grid_sfc = pv.grid_from_sph_coords(xx_bounds, yy_bounds, levels)
grid_sfc.cell_arrays["laf"] = np.array(laf.sftlf.values).swapaxes(-2, -1).ravel("C")

# Grid for modelling centres
# create 0s xarray and add 1s where modelling centres exist
xr_centres = xr.zeros_like(laf.sftlf)
df['lon'][df.lon < 0] = [ 360 + i for i in df.lon[df.lon < 0] ]
df['lat_pos'] = [ np.where(abs(laf.lat - i) == np.min(abs(laf.lat - i)))[0][0] for i in df.lat ]
df['lon_pos'] = [ np.where(abs(laf.lon - i) == np.min(abs(laf.lon - i)))[0][0] for i in df.lon ]
for lt, ln in zip(df.lat_pos, df.lon_pos): xr_centres[lt, ln] = 1
# make pv grid and add array
levels = [RADIUS * 1.011]
grid_centres = pv.grid_from_sph_coords(xx_bounds, yy_bounds, levels) 
grid_centres.cell_arrays["centres"] = np.array(xr_centres.values).swapaxes(-2, -1).ravel("C")

# Make a plot, open movie
p = pv.Plotter()
p.add_mesh(pv.Sphere(radius=RADIUS))

# Global surface 
p.add_mesh(grid_sfc, clim=[0.1, 2.0], cmap="ocean_r", show_scalar_bar=False)# smooth_shading=False
p.add_mesh(grid_centres, clim=[0.1, 2.0], cmap='Reds', show_scalar_bar=False, opacity = 0.5) # style='wireframe', opacity=0.2) 

p.show(auto_close=False) # close with q on keyboard and then gif will generate 

''' Uncomment these lines to create gif. Will need to close pyvista IDE with q before gif will generate
filename = 'C:/Users/vanvlietL/Documents/Animations/GCM_wiremesh.mp4'
p.open_movie(filename, framerate=24) # movie is smaller than gif 
#p.open_gif(filename)

path = p.generate_orbital_path(n_points=360, viewup=[0, 0, 1], shift=6) # viewup controls orbital plane, shift controls view
p.orbit_on_path(path, write_frames=True) #focus=None, step=0.5 --> camera focus, timestep 
p.close()
'''
# To save image
#flon, flat = 270, 40 # focus 
#p.set_position(pv.grid_from_sph_coords(flon, [90 - flat], [8*RADIUS]).points)  # default: [(5.485199280057733, 5.485199280057733, 5.485199280057733),
#p.set_focus((0, 0, 0))
#p.set_viewup((0, 1, 0)) # default: 0, 0 ,1

#p.show(screenshot=imgname, auto_close=False) # to simply save jpeg of image