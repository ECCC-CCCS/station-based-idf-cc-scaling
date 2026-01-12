# -*- coding: utf-8 -*-
"""

## files are monthly (1-12) annual (13) and seasonal (winter14-fall17)

## file names have been set up to follow the nomenclature used by Dave Benoit

lat and lons are provided for every corner in CANGRD_points_LL.csv (read in as pts below)

From CanGRD docs:
"where the SW corner (0,0) is at 40.0451°N latitude and 129.8530°W longitude. The projection is true at 60.0°N and centered on 110.0°W." 
Proj4string from OpenCanada "+proj=stere +lat_0=90 +lat_ts=60 +lon_0=-110 +x_0=1884770 +y_0=5220000 +datum=WGS84 +to_meter=50000"

"""

### still need to do precip and trends
import glob, os
import rasterio
import pandas as pd
import sys
sys.path.insert(0, '/***REMOVED***/***REMOVED***/cccs-utilities/data-tools')
import spatial_reprojector
from pyproj import CRS
import matplotlib.pyplot as plt
import numpy as np

### Read in points file to be lat and lon values
pts = pd.read_csv('CanGRD_Points_LL.csv', header = None)
pts.columns = ['a', 'b', 'lat', 'lon']

#Generate x,y (m/m) values from input lat/lon values
x,y=spatial_reprojector.latlon2grid(pts['lat'],pts['lon'],'epsg:3995')
#x=np.reshape()
#y=np.reshape()

plt.plot(pts['lat'])
plt.savefig('lat.png')

ras = rasterio.open('t190001.grd', masked = True )
test=ras.read(1)
ras.crs['init']="+proj=stere +lat_0=90 +lat_ts=60 +lon_0=-110 +x_0=1884770 +y_0=5220000 +datum=WGS84 +to_meter=50000"
print(ras)


