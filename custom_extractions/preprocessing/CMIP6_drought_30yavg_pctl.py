# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 14:45:19 2025

@author: VanVlietL
"""

import os
import numpy as np
import xarray as xr
import gc
import pandas as pd
import glob
from filepaths import filepaths 
from xclim import ensembles
#%%

scales = ['_scale3', '_scale12']
dummy_scales = ['']
ssps = ['ssp126', 'ssp245', 'ssp585', 'ssp370']

scale_dict = {'SRI_surface': scales,
              #'SRI_total': scales, # name has been changed to "SRI_total_notonCCDS" need to update script
              'SSI_surface': scales,
              'SSI_total': scales, 
              'SPEI': scales,
              'mrro': dummy_scales,
              'mrros': dummy_scales,
              'mrso': dummy_scales,
              'mrsos': dummy_scales 
              }

# Functions for data formatting. These allow proper % change calculation on subannual indices.
def unstack_time(ds):
    '''
    Assign year and month as coords, replacing the single time dimension.
    This allows stats to be calculated on single month/season, similar to groupby functionality.
    
    Parameters
    ----------
    ds : xr dataset or datarray with time dimension (datetime format)

    Returns
    -------
    ds : xr dataset/array where time has been replaced with two new dims: month and year
    '''
    # assign new coords
    ds = ds.assign_coords(year=("time", ds.time.dt.year.data),
                          month=("time", ds.time.dt.month.data))
    # replace time with 'year' and 'month' as dims
    ds = ds.set_index(time=("year", "month")).unstack("time")  
    return ds
    
def restack_time(ds):
    '''
    Restack month and year coords into a single 'time' dimension with datetime index

    Parameters
    ----------
    ds : xarray dataaset with month and year coords instead of 'time' dimension
        
    Returns
    -------
    ds : xarray dataset where month and year have been restacked into one dimension with datetime format.

    '''
    ds_stacked = ds.stack(time=('year','month'))
    datetimes = pd.to_datetime([f'{year}-{month:02d}-01' for year, month in ds_stacked.time.values])
    ds_stacked = ds_stacked.drop_vars(['time', 'year', 'month'])
    ds_stacked = ds_stacked.assign_coords(time=datetimes)  
    return ds_stacked

# function for open_mfdataset to allow ensemble creation over realization dimension
def add_model_dim(ds):
    flnm = os.path.basename(ds.encoding['source']) # get filename (unique to each model) from dataset encoding
    # add realization as a dimension on the dataset, using flnm as realization name
    ds = ds.assign_coords(realization=flnm).expand_dims('realization')

    # align and fix calendars to allow concat
    # some models were saved with time units 'days since 1850' and calendars other than no leap.
    # by 1950, the date that should be decoded at 1950, is decoded in 1949, and other future dates are also in incorrect months.
    assert len(ds.time) == 1812, f'The time axis is not monthly for {flnm}, there are {len(ds.time)} records' # check that the time-axis is monthly
    new_time = xr.date_range(start='1950-01-01',
                             periods=len(ds.time),
                             freq='MS')
     
    # Update the time coordinate in the dataset
    ds['time'] = new_time
    # there are some rounding differences in lon dim, adjust
    if metric == 'SPEI':
        ds = ds.rename({'longitude': 'lon', 'latitude': 'lat'})
    ds['lon'] = ds.lon.values.round(2)
               
    for var in ['time_bnds','lon_bnds','lat_bnds', 'depth', 'depth_bnds']:
        try:
            ds = ds.drop_vars(var) # some metrics/models have these, but not all
            #print(f'{var} dropped for {flnm}')
        except ValueError:
            pass
               
    return ds

def remove_mods(lst, mods):
    '''Remove models for select indices so ensemble matches documentation
    https://climate-scenarios.canada.ca/?page=cmip6-drought-notes#table-2
    but also excludes models without SSP370 runs'''
    for mod in mods:
        lst = [i for i in lst if mod not in i]
    return lst
#%%
for metric, scales in scale_dict.items():

    print(f'.... {metric}')

    for ssp in ssps: 
        
        print(f'.............. {ssp}')
        
        for scale in scales:
        
            print(f'..................... {scale}')    
        
            # create directory for this metric, frequency, and ssp 
            outpath = f'{filepaths.workspace}/CMIP6_drought/'
            
            inpath = f'{filepaths.CMIP6_drought}/{metric}/' # input data location
            ens_files = glob.glob(f'{inpath}/*{metric}*{scale}*{ssp}*.nc')
            
            if metric in ['SPEI', 'SRI_surface', 'SRI_total', 'SSI_surface', 'mrro', 'mrros', 'mrsos']:
                ens_files = remove_mods(ens_files, ['KIOST', 'HadGEM3']) # These models not availabe for RCP370
                ensemble_size = 23           
            elif metric in ['SSI_total', 'mrso']:
                ens_files = remove_mods(ens_files, ['KIOST', 'HadGEM3', 'KACE']) # These four models not availabe for some or all RCPs
                ensemble_size = 22         
            
            # rather than using xclim.ensembles, create ensemble manually with open_mfdataset and a preprocess to add the realization dimension.
            # open_mfdataset does not automatically pad with NaNs or align calendar, to better catch potential errors
            # it also has better handling of attrs (where xclim takes attrs from the first dataset)
            ensemble = xr.open_mfdataset(ens_files, decode_times=False, # open data using decode_times = False b/c there is an issue with the calendar for some files that needs to be fixed
                                         preprocess=add_model_dim, # preprocess adds model (called realization) as a dimension
                                         join='exact', # "raise ValueError when indexes to be aligned are not equal"
                                         combine_attrs="drop_conflicts", # "attrs from all objects are combined, any that have the same name but different values are dropped."
                                         data_vars=[metric.lower()], # this will make sure things line time_bnds are not loaded (since they're not on all models)
                                         ).chunk({'realization':-1}) # "-1" will create one large chunk along realization dim to allow for ens percentiles 
                
            # check to make sure all files/model runs exist
            assert len(ensemble.realization) == ensemble_size, f'There are only {len(ensemble.realization)} ensemble members, not {ensemble_size}: \n {ens_files}'
            
            if metric in ['SRI_surface', 'SSI_surface','SRI_total', 'SSI_total','SPEI']:
                # Apply unstack_time to replace time dim with 'year' and 'month' coords
                ensemble = unstack_time(ensemble)
                # take 30 year rolling means, note: it is labelled by the RIGHT EDGE (end of 30 year period) of the window
                ensemble = ensemble.rolling(year=30, min_periods=20, center=False).mean(keep_attrs=True) # LV FIX: set min_periods=20 as a workaround for missing values in SPEI, SSI and SRI model files. See csv file for example
                # define windows to keep, using the end year of the 30 year window ending each decade
                windows_keep = np.arange(1980,2101,10)
                ensemble = ensemble.sel(year=ensemble.year.isin(windows_keep)) # this will keep all months in specified years
                ensemble['year'] = [int(ii-29) for ii in ensemble.year.values] # relabel to first year in period for rebuilding time axis
                ensemble = restack_time(ensemble)        
            else:
                ensemble = ensemble.sel(lat=slice(40.5,89.5), lon=slice(190.5,309.5))
                # call xr.resample, offsetting by 10-years 3 times, to allow for all periods to be generated
                ensemble = xr.merge([ensemble.sel(time=slice('1951','2100')).resample(time='30YS', closed='left', label='left').mean(keep_attrs=True, skipna=False), # will calc periods starting in 1951, 1981, 2011, 2041, 2071
                                     ensemble.sel(time=slice('1961','2100')).resample(time='30YS', closed='left', label='left').mean(keep_attrs=True, skipna=False), # will calc periods starting in 1961, 1991, 2021, 2051
                                     ensemble.sel(time=slice('1971','2100')).resample(time='30YS', closed='left', label='left').mean(keep_attrs=True, skipna=False) # will calc periods starting in 1971, 2001, 2031, 2061
                                     ]).sel(time=slice('1951','2071'))
                scale = '_YS'
                             
            ens_percentiles = ensembles.ensemble_percentiles(ensemble, # call xclim ensemble percentiles func
                                                             min_members=None, # minimum number of valid ensemble members for a statistic to be valid. Setting to "None" set it to the size of realization dimension. 
                                                             # Should not be an issue, assuming there are no problems w data
                                                             values=[10, 50, 90], # percentiles to calculate
                                                             split=True, # split each percentile into a new variable
                                                             method='linear') # the default method for estimating percentile, adding here for clarity. 
            
            ## setting split=True above copies variable attrs to file attrs. delete duplicate var attrs from file attrs 
            for attr in ens_percentiles[f'{metric.lower()}_p10'].attrs: 
                if attr == 'description':
                    continue
                del(ens_percentiles.attrs[attr])
            
            ens_percentiles = ens_percentiles.transpose("time", "lat", "lon") # reorder dims to match CF-preferred ordering to T-Y-X
            
            # set encoding 
            encoding = {var: {'dtype': 'float32',
                              'zlib': True, # compress outputs
                              'complevel': 5, # 1 to 9, where 1 is fastest, and 9 is maximum compression
                              '_FillValue': 1e+20, # missing value depreciated, not added
                              'chunksizes': [len(ens_percentiles.time), 20, 20]
                              } for var in ens_percentiles.data_vars} 
            
            # save
            ens_percentiles.to_netcdf(f'{outpath}/{metric}{scale}_historical+{ssp}_1950-2100_30ymean_percentiles.nc', 
                                      encoding=encoding)
        
            # free up memory
            del([ens_files, ensemble, ens_percentiles])
            gc.collect()

print('All ensemble percentiles calculated!')
