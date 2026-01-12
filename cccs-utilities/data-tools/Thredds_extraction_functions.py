# -*- coding: utf-8 -*-
"""
Created on Wed May 26 13:49:36 2021

@author: ChowK
"""

import os
from typing import List, Optional, Sequence, Union
import xarray as xr
from clisops.core import subset
import pandas as pd
import threddsclient
from xclim import ensembles
import geopandas as gpd
import numpy as np
import datetime
import time
start_time = time.time()

#%%
def threddscall(em_scenarios: str,
                indices: str,
                frequency: str = 'YS',
                average: bool = False,
                cmip6: bool = True,
                models: List[str] = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'BCC-CSM2-MR', 'CMCC-ESM2', 'CNRM-CM6-1', 'CNRM-ESM2-1', 
                                     'CanESM5', 'EC-Earth3-Veg', 'EC-Earth3', 'FGOALS-g3', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 
                                     'INM-CM4-8', 'INM-CM5-0', 'IPSL-CM6A-LR', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2L', 'MIROC6',
                                     'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'NorESM2-LM', 'NorESM2-MM', 'TaiESM1', 
                                     'UKESM1-0-LL']):
    """Extracts and saves a list of links from the PAVICS Thredds server
    
    Parameters
    ----------
    em_scenarios : str
      String of desired emission scenarios
    
    indices : str
      String of desired indices to query and extract from the Thredds server
      
    frequency : str
      Frequency for thredds to specify extracting yearly or monthly data. Defaults to yearly data
    
    average : List[bool]
      Boolean indicating whether whether or not 30-year averages should be extracted
    
    cmip6 : bool
      Boolean indicating whether to use CMIP6 data or not. Adjusts the base link and is defaulted to CMIP6. When labeled False it will allow for CMIP5 use.
      
    models : List[str]
      List of desired models. Defaults to the 26 models used in standard CanDCS-M6/ClimateData.ca ensemembles. If CMIP6 argument is set to False, then it will use all 24
      models from the BCCAQv2/ClimateData.ca ensembles.
      
    Returns
    -------
    list_fld : List[nodes.DirectDataset]
      List containing nodes to the datasets
      
    """
    # Create a default list of models set to the CMIP6 models. Which in the event that the user wishes to use specific models from CMIP5 they can.
    defaultModels = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'BCC-CSM2-MR', 'CMCC-ESM2', 'CNRM-CM6-1', 'CNRM-ESM2-1', 
                                     'CanESM5', 'EC-Earth3-Veg', 'EC-Earth3', 'FGOALS-g3', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 
                                     'INM-CM4-8', 'INM-CM5-0', 'IPSL-CM6A-LR', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2L', 'MIROC6',
                                     'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'NorESM2-LM', 'NorESM2-MM', 'TaiESM1', 
                                     'UKESM1-0-LL']
    # First determine if the user is wanting CMIP6 or CMIP5 data, and adjust the base URL to reflect as such
    if cmip6:
        baseUrl = "https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/birdhouse/disk2/cccs_portal/indices/Final/CanDCS-M6/"
    else:
        # Base url for CMIP5
        baseUrl = "https://pavics.ouranos.ca/thredds/catalog/birdhouse/disk2/cccs_portal/indices/Final/BCCAQv2/"
        # Reset to the base models.
        if models == defaultModels:
          # If the user set models are equal to the default ones, then the user did not specify which CMIP5 models they wanted.
          # Reseting the default to the 24 models from BCCAQv2/ClimateData.ca.
          models = ['BNU-ESM', 'CCSM4', 'CESM1-CAM5', 'CNRM-CM5', 'CSIRO-Mk3-6-0', 'CanESM2', 'FGOALS-g2', 'GFDL-CM3',
                                     'GFDL-ESM2G', 'GFDL-ESM2M', 'HadGEM2-AO','HadGEM2-ES', 'IPSL-CM5A-LR', 
                                     'IPSL-CM5A-MR', 'MIROC-ESM-CHEM', 'MIROC-ESM', 'MIROC5', 'MPI-ESM-LR',
                                     'MPI-ESM-MR', 'MRI-CGCM3', 'NorESM1-M', 'NorESM1-ME', 'bcc-csm1-1-m', 'bcc-csm1-1']
    #Determines whether user is accessing annual, 30y annual means, monthly, 30y monthly means, or daily data
    if not average:
        if frequency == 'DS':
            url = "https://pavics.ouranos.ca/thredds/catalog/birdhouse/pcic/BCCAQv2/catalog.html"
        else:
            url = f"{baseUrl}/{indices}/{frequency}/{em_scenarios}/simulations/catalog.html"
    else:
        url = f"{baseUrl}/{indices}/{frequency}/{em_scenarios}/simulations_30yAvg/catalog.html"
  
    list_fld = []
    for m in models:
        ncfiles = [ds for ds in threddsclient.crawl(url, depth=10) if m + '_' in ds.name] #crawls through the thredds directories to get the openDAP url of the sought after model
        for n in ncfiles:
            if indices in n.name and em_scenarios in n.name: #further sorts the urls for filtering
                list_fld.append(n)
    return list_fld

#%%

def unit_coversion(ds: xr.DataArray, index: str):
    """Converts units of indices to standard units (nanosecods -> days and Kelvin -> Celcius)
    
    Parameters
    ----------
    ds : xr.DataArray
      Dataset object for unit conversion
     
    index : str
      Variable/Index name
      
    Returns
    -------
    ds_converted : xr.DataArray, [Days, or degC]
    
    """  
    
    varsDays=['txgt_32', 'txgt_30', 'txgt_29', 'txgt_27', 'txgt_25', 'tr_24', 'tr_22', 'tr_20', 
              'tr_18', 'tnlt_-25', 'tnlt_-15', 'r20mm', 'r1mm', 
              'r10mm', 'ice_days', 'frost_days', 'frost_free_season']
    
    varsTemp=['tx_mean', 'tx_max','tn_min', 'tn_mean', 'tg_mean', 'tx_min', 'tn_max']
    
    #nanosecond timedelta64 objects to Days
    if index in varsDays:
        ds = ds / np.timedelta64(1, 'D')
        ds[index].attrs['units'] = 'Days'
        print("xr opened, timedelta decoded False")
    #Kelvin to Celsius                
    elif index in varsTemp:
        ds = ds -273.15
        ds[index].attrs['units'] = 'degC'
        print("xr opened, converted K to C")
    else:
        ds = ds
        
    return ds
            
#%%
def index_extract(model: str,
                  index: str,
                  first_date: str,
                  last_date: str,
                  m: bool = False,
                  months: List[int] = list(range(1,13)),
                  subset: str = ""):
                  
                  
    """Extracts data from the PAVICS Thredds server
    
    Parameters
    ----------
    model : str
      String of the thredds URL of the model on OpenDAP
      
    index : str
      String of desired index
    
    first_date : str
      String of the first date for the dataset
      
    last_date : str
      String of the last date for the dataset
               
    Returns
    -------
    ds : xr.DataArray
      DataArray of extracted index
      
    """
   
    print(model)
    r=str(model.opendap_url())
    ds = xr.open_dataset(r)
    #check flag for monthly data and extracts desired months, otherwise selects all data
    if m == True:
        ds = ds.sel(time=ds.time.dt.month.isin(months)).sel(time=slice(first_date,last_date))
    else:
        ds = ds.sel(time=slice(first_date,last_date))
    #convert to appropriate units
    ds = unit_coversion(ds, index)
    ds.close() 
    return ds           

#%%    
def region_select(ds, polygon, identifier, region):

    """Selects the sub region from a shapefile and spatially means the values
    
    Parameters
    ----------
    ds : xr.DataArray
      Xarray dataset 
      
    polygon : .shp
      shapefile
    
    identifier : str
      Column name of the different region names
      
    region : str
      region name that you want to select/spatially average
               
    Returns
    -------
    ds_Mean : xr.DataArray
      DataArray of extracted index
      
    """
    #ds = ds.salem.roi(shape=polygon.loc[polygon[identifier] == region]).drop_vars('crs') #spare lines for older versions where clisops.core.subset is not available
    ds = subset.subset_shape(ds, polygon.loc[polygon[identifier] == region]).drop_vars('crs')
    ds_Mean = ds.mean(dim=['lat','lon'], keep_attrs = True)
    return ds_Mean        

#%%    
def average_30y(ds, first_date, last_date):

    """Selects the desired time period and temporally means the values
    
    Parameters
    ----------
    ds : xr.DataArray
      Xarray dataset 
      
    first_date : str
      String of the first date for the 30y avg
      
    last_date : str
      String of the last date for the 30y avg
               
    Returns
    -------
    ds30yavg : xr.DataArray
      DataArray temporally averaged
      
    """

    ds_slice = ds.sel(time=slice(first_date, last_date))
    cft = ds_slice.time.isel(time=0) #ClimateData.ca 30y averages are timestampled for the beginning of the 30y period (i.e., 1981-2010 would be dated 1981-01-01)
                                     #Once you do a mean over a dimension, e.g., time, the dimension will no longer exist
                                     #This line keeps a copy of the timestamp to add back later     
    ds30yavg = ds_slice.mean('time', keepdims = False, keep_attrs = True).assign_coords({'time':cft}) # adds back the timestamp so the 30y average has a time dimension
    return ds30yavg

#%%            
def custom_ensemble(ds_list, percentiles = [10,50,90]):

    """Selects the desired time period and temporally means the values
    
    Parameters
    ----------
    ds_list : list of xr.DataArray
      A list of xr.DataArray objects to take an ensemble over 
      
    percentiles : list of int
      A list of the percentiles to take the ensemble over, defaults to 10th, 50th and 90th
               
    Returns
    -------
    ens_perc : xr.DataArray
      DataArray of the 10th, 50th, and 90th percentiles of the 24 model ensemble for the variable
      
    """

    ens = ensembles.create_ensemble(ds_list).load()           
    ens_perc = ensembles.ensemble_percentiles(ens, values=percentiles, split=True)
            
    return ens_perc        

#%%            
def main():
    #Dummy calls - can modify for real use if required
    print("There are 6 functions in this script that are used in variations of client-requested extractions:")
    print("threddscall - access the PAVICS thredds server and get the openDAP URLs for the datasets desired")
    print("unit_coversion - converts time units from nanosecond timedelta64 objects to days and Kelvin units to Celsius")
    print("index_extract - pulling the data from the server and opening the dataset in python and convert to appropriate units if required")
    print("region_select - subsetting a spatial region for a spatial mean")
    print("average_30y - calculating 30y means")
    print("custom_ensemble - aggregate model output and computes ensemble percentiles")

if __name__ == "__main__":
    main()        

            
            
            
            
            
            
            
            
            
            