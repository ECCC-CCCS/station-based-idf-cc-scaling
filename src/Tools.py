########## Tools.py ##########
# This script contains code for functions that I created that were useful,
# but maybe did not fit into the other scripts catecorgically.
# - Jaxton Gray
##############################
import sys, os
import numpy as np
import xarray as xr
# CCCS Utility tools that must be installed first, or placed inside directory
sys.path.append('cccs-utilities/data-tools')
sys.path.append('../cccs-utilities/data-tools')
sys.path.append('../custom_extractions')
from ECCC_IDF_reader import read_ECCC_IDF
from custom_extractions.functions import closest_node
#%%
# Reformat_historical_IDF
def reformat_historical_IDF(file_list: list[str]) -> xr.Dataset:
    """Combines all historical IDF data into one xarray dataset
    
    Parameters
    ----------
    file_list : list[strings]
        List containing path locations of historical IDF files
    
    Returns
    -------
    histIDF : xarray.Dataset
        Xarray dataset containg the the combined historical IDF data information
    
    """
    # Cycle through each file and extract the data
    da_list = [] # Initialize an empty list to hold dataarrays of the files
    con_list = []
    lat_list = []
    lon_list = []
    stn_list = []
    for file in file_list:
        # Grab the IDF info from each file
        dictIDF = read_ECCC_IDF(file)
        stationID = dictIDF['location']['ID']
        
        # Add xarray dataarrays into the correspinding lists
        da_list.append(xr.DataArray(
            dictIDF['IDF_rates'].replace(-99.9, np.nan),
            dims=('duration', 'return_period')).assign_coords(
                {'station':stationID}))
        
        con_list.append(xr.DataArray(
            dictIDF['IDF_rate_confidence'].replace(-99.9, np.nan),
            dims=('duration', 'return_period')).assign_coords(
                {'station':stationID}))
        
        lat_list.append(xr.DataArray(
            dictIDF['location']['latitude']
            ).assign_coords(
                {'station':stationID}))
                
        lon_list.append(xr.DataArray(
            dictIDF['location']['longitude']
            ).assign_coords(
                {'station':stationID}))
                
        stn_list.append(xr.DataArray(
            dictIDF['location']['name']
            ).assign_coords({'station':stationID}))
        
    # Concatenate each list in one big DataArray based on the station dimmension
    daArr = xr.concat(da_list, dim='station')
    conArr = xr.concat(con_list, dim='station')
    latArr = xr.concat(lat_list, dim='station')
    lonArr = xr.concat(lon_list, dim='station')
    stnArr = xr.concat(stn_list, dim='station')
    
    # Make one Xarray Dataset from each of the DataArrays
    histIDF = xr.Dataset(dict(
        IDF_data=daArr,
        IDF_confidence=conArr)
        ).assign_coords(dict(
            station_name=stnArr,
            lat=latArr,
            lon=lonArr))
    
    return histIDF
#%%
# Function that will make use of the closest_node function and look for the nearest
# grid with data up to set number of grids away

def next_nearest_grid(ds, site_lat, site_lon, numGrids_Search=5):
    # Start a loop to check iteratively if the dataset is null at the given point
    for r in range(1, numGrids_Search+1):
        # Run through the current grid
        output = closest_node(ds, site_lon, site_lat, radius=r)

        if not bool(output.isnull().all()):
            # If output is not completely null break, and return the output
            return output
        else:
            # If still null return the dataset at those coordinates
            output = ds.sel(lat=site_lat, lon=site_lon, method='nearest')

    return output

