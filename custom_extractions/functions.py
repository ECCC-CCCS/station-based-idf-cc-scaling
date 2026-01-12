# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 14:59:49 2022

@author: VanVlietL, edited by evagnegy
"""

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
import xarray as xr

def rm_comma(x):
    if x[-1]==',':
        out = x[:-1]
    else:
        out = x
    return out

def get_csv(flnm):
    try: 
        df = pd.read_csv(flnm, encoding='iso-8859-1',  sep=';', quotechar='"', engine='python', index_col=['FederalSiteIdentifier'])  
    except ValueError:
        df = pd.read_csv(flnm, encoding='iso-8859-1',  sep=',', quotechar='"', engine='python', index_col=['FederalSiteIdentifier'])  
    #print(df)
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    #print(df.shape)
    try: 
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    except KeyError: 
        try: 
            df['Longitude'] = pd.to_numeric(df["Longitude,"].apply(rm_comma), errors='coerce')
        except TypeError: 
            df['Longitude'] = pd.to_numeric(df["Longitude"].apply(rm_comma), errors='coerce')
    #print(df.Longitude.values)
    return df

def dist(lat,lon,latI,lonI):
    R = 6371   #radius of earth
    dlon = (lon - lonI) * np.pi/180
    dlat = (lat - latI) * np.pi/180
    ilat = latI * np.pi/180
    flat = lat * np.pi/180
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.sin(dlon/2) * np.sin(dlon/2) * np.cos(ilat) * np.cos(flat) 
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)) 
    out = R * c
    return out


def closest_node(ds,site_lon,site_lat,radius=1):
    """Utility function to select next closest grid in case the closest grid to station has no data
    
    Parameters
    ----------
    ds : xr.Dataset
      Original dataset object 
     
    site_lon : float
      Longitude coordinate of the station/site in decimal degrees, -180 to 180
    
    site_lat : float
      Latitude coordinate of the station/site in decimal degrees, -90 to 90

    Returns
    -------
    ds_site : xr.Dataset - dataset object of the next closest grid with non-missing data
    
    Notes
    -------
    Currently configured to look for the next closest, ONE (1) grid (10km) away.
    Can be configured to look up to 2 grids away, but this is not recommended as
    the data for a grid 20 Km away may not be representative of the site of interest.
    (This was done for the FCSAP extraction, but the handful of sites were clearly noted,
    and subject to removal) 
    
    """  
    #find the indices of the lat lon of the closest grid as our centre
    centrallonIndex = list(ds.lon.values).index(ds.sel(lon=site_lon, method='nearest').lon)
    centrallatIndex = list(ds.lat.values).index(ds.sel(lat=site_lat, method='nearest').lat)
    node = np.array([[site_lon],[site_lat]]) #node of interest is the actual site
    nodes=[]
    
    #following nested loop finds all the grids 1 grid radius away from centre (total of 9 grids)
    for a in range(-radius, radius+1):
        for b in range(-radius, radius+1):
            #Check to see if the central grid is located at the edges of the dataset (therefore no adjacent grids)
            #if not, business as usual
            if (not (centrallonIndex+a > len(ds.lon)-1 or centrallonIndex+a < 0) and not (centrallatIndex+b > len(ds.lat)-1 or centrallatIndex+b < 0)):  
                ds_temp=ds.isel(lon=centrallonIndex+a,lat=centrallatIndex+b)
            #otherwise, adds the central grid as replacement, dummy grids
            else:
                ds_temp=ds.isel(lon=centrallonIndex,lat=centrallatIndex)
            nodes.append([ds_temp.lon.values,ds_temp.lat.values]) #compile a list of coordinates of adjacent grids
    nodes = np.asarray(nodes)
    
    #convert to cartesian coordinates and look up nearest neighbour using cKDTree and tree.query
    xs, ys, zs = lon_lat_to_cartesian(nodes[:,0], nodes[:,1])
    xt, yt, zt = lon_lat_to_cartesian(node[0], node[1])
    tree = cKDTree(np.array(list(zip(xs, ys, zs))))
    d, inds = tree.query(np.array(list(zip(xt, yt, zt))), k=(2 * radius + 1) ** 2)
    
    #Loop through the ordered list of closest neighbours and verify that the grid has data
    for i in range(0,len(inds[0])):
        lon_new=nodes[inds[0][i],0]
        lat_new=nodes[inds[0][i],1]
        ds_site = ds.sel(lon=lon_new,lat=lat_new).drop_vars(['lat','lon'])
        #if the selected closest grid has no missing data,end the verification loop
        if not np.all(np.isnan(ds_site.tg_mean.values.flatten())):
            break
    return ds_site



def lon_lat_to_cartesian(lon, lat, R = 1):
    """calculates lon, lat coordinates of a point on a sphere with radius R
    
    Parameters
    ----------
    lon : float
      Longitude coordinate in decimal degrees, -180 to 180
     
    lat : float
      Latitude coordinate in decimal degrees, -90 to 90

    R : float
      Radius of the earth, defaults to 1 and should not be changed unless for specific purposes

    Returns
    -------
    x,y,z : float, [cartesian coordiates]
    
    """ 
    #convert decimal degrees to radians
    lon_r = np.radians(lon)
    lat_r = np.radians(lat)
    
    #convert radians to cartesian coordinates
    x = R * np.cos(lat_r) * np.cos(lon_r)
    y = R * np.cos(lat_r) * np.sin(lon_r)
    z = R * np.sin(lat_r)
    return x,y,z
