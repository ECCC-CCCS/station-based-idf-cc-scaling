# -*- coding: utf-8 -*-
"""
Author: Laura Van Vliet
Date: July 2, 2025 

Calculate percentage change for all CanDCS-M6 indices with base zero (that is, excluding temperature indices w units of degC or K, or indices w dates).
This is done by model using 30-year averages of indices from PAVICS Thredds, and then saved to GPSC.

CanDCS-M6 indices to calculate: 
    ['ccdcold_18',
     'cdd',
     'dlyfrzthw_tx0_tn-1',
     'frost_days',
     'frost_free_season',
     'gddgrow_0',
     'gddgrow_5',
     'hddheat_18',
     'ice_days',
     'nr_cdd',
     'prcptot',
     'prsntot',
     'r10mm',
     'r1mm',
     'r20mm',
     'rx1day',
     'rx5day',
     'sn10mm',
     'sn2mm',
     'snowfall_season_length',
     'snx1day',
     'tnlt_m15',
     'tnlt_m25',
     'tr_18',
     'tr_20',
     'tr_22',
     'txgt_25',
     'txgt_27',
     'txgt_29',
     'txgt_30',
     'txgt_32']


CanDCS-M6 indices which are not calculated (units of degC, K, or dates): 
    'tn_mean', 'tn_min', 'tg_mean', 'tx_mean', 'tx_max', 
    'first_fall_frost','last_spring_frost', 'last_snowfall'  


Other indices to calculate: (future script update)
    Humidex: 'HXmax30', 'HXmax35', 'HXmax40' (https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/birdhouse/eccc/CCCS_humidex/Humidex/catalog.html)
    SLR: https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/catalog/birdhouse/disk2/cccs_portal/indices/Final/SEA_LEVEL_RISE/catalog.html

"""

import os
import sys
import numpy as np
import xarray as xr
import gc
import pandas as pd
import datetime
from filepaths import filepaths 

metric = sys.argv[1] # one of the CD.ca vars above, from run file

# Dictionary of scales for which metrics were calculated (annual, seasonal, monthly). Not all indices have subannual indices.
freq_dict = {'cddcold_18': ['YS'],
             'cdd': ['YS'],
             'dlyfrzthw_tx0_tn-1': ['YS'],
             'frost_days': ['YS'],
             'frost_free_season': ['YS'],
             'gddgrow_0': ['YS', 'MS'],
             'gddgrow_5': ['YS'],
             'hddheat_18': ['YS'],
             'ice_days': ['YS'],
             'nr_cdd': ['YS', 'MS'],
             'prcptot': ['YS', 'QS-DEC', 'MS'],
             'prsntot': ['YS', 'QS-DEC', 'MS'],
             'r10mm': ['YS', 'QS-DEC', 'MS'],
             'r1mm': ['YS', 'QS-DEC', 'MS'],
             'r20mm': ['YS', 'QS-DEC', 'MS'],
             'rx1day': ['YS', 'QS-DEC', 'MS'],
             'rx5day': ['YS', 'MS'],
             'sn10mm': ['YS', 'QS-DEC', 'MS'],
             'sn2mm': ['YS', 'QS-DEC', 'MS'],
             'snowfall_season_length': ['YS-JUL'], # YS-JUL is annual, where year starts in summer
             'snx1day': ['YS', 'QS-DEC', 'MS'],
             'tnlt_m15': ['YS', 'MS'],
             'tnlt_m25': ['YS', 'MS'],
             'tr_18': ['YS', 'MS'],
             'tr_20': ['YS', 'MS'],
             'tr_22': ['YS', 'MS'],
             'txgt_25': ['YS', 'MS'],
             'txgt_27': ['YS', 'MS'],
             'txgt_29': ['YS', 'MS'],
             'txgt_30': ['YS', 'MS'],
             'txgt_32': ['YS', 'MS']
             }

frequency_scales = freq_dict[metric] # get the list of scales for the metric of interest

# dictionary of frequency labels used in filenames versus folder structure
freq_label = {'YS': 'ann',
              'QS-DEC': 'sea',
              'MS': 'mon',
              'YS-JUL': 'ann-juljun'}

ref_periods = ['1971', '1981'] # list of reference periods to calculate % change from. Represents first year of 30 year period (e.g., 1971-2000)

# dict to match time horizon/period to first year of ref period for variable attrs, etc
horizon1 = {'1971': '1971_2000', 
            '1981': '1981_2010'} 
horizon2 = {'1971': '1971-2000', 
            '1981': '1981-2010'} 
     
ssps = ['ssp126', 'ssp245', 'ssp370', 'ssp585']    
    
# all available models for CMIP6 CanDCS-M6
models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'BCC-CSM2-MR', 'CMCC-ESM2', 'CNRM-CM6-1',
          'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-Veg', 'EC-Earth3', 'FGOALS-g3', 'GFDL-ESM4',
          'INM-CM4-8', 'INM-CM5-0', 'IPSL-CM6A-LR', 'KIOST-ESM',
          'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'NorESM2-LM', 
          'NorESM2-MM', 'TaiESM1', 'HadGEM3-GC31-LL', 'UKESM1-0-LL', 'KACE-1-0-G']

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
    datetimes = pd.to_datetime([f'{year}-{month:02d}-01' for 
                               year, month in ds_stacked.time.values])
    ds_stacked = ds_stacked.drop_vars(['time', 'year', 'month'])
    ds_stacked = ds_stacked.assign_coords(time=datetimes)  
    return ds_stacked


# Loop through models calculating percentage change and saving to netCDF
for freq in frequency_scales:
 
    print(f'.............. {freq}')
    
    for ssp in ssps:
    
        # create directory for this metric, frequency, and ssp 
        outpath = f'{filepaths.M6_outpath}/{metric}/{freq}/{ssp}/simulations_30yAvg/'
        os.makedirs(outpath, exist_ok=True)
        
        for mod in models:  
                    
            print(f'..................... {ssp} {mod}')
            
            if mod in ['HadGEM3-GC31-LL', 'KIOST-ESM'] and ssp == 'ssp370': # these two models not avail for ssp370, pass
                continue
                
            if metric in ['prsntot', 'sn10mm', 'sn2mm', 'snowfall_season_length', 'snx1day']: 
                date_string = '1951-2100' # filenames named differently for snow vars
            else: 
                date_string = '1950-2100'
            
            filename = f'{filepaths.CanDCS_M6_indices}{metric}/{freq}/{ssp}/simulations_30yAvg/' \
                       + f'{metric}_{freq_label[freq]}_MBCn+PCIC-Blend_{mod}_historical+{ssp}_{date_string}_30ymean.nc'
          
            dat = xr.open_dataset(filename, decode_timedelta=False) # open data using decode_time = False so that count-based indices (units of days) are not converted to timedelta objects
            
            dct = {} # empty dictionary to save changes from dif ref periods
            
            for ref_period in ref_periods:
                
                ref = dat[metric].sel(time=ref_period) # get reference period absolute values. xr will select all dates in "ref_period" year (if YS=1, if MS=12, if QS-DEC=4)
                
                if freq in ['YS', 'YS-JUL']: # for indices calculated annually
                    ref = ref.squeeze().drop_vars(['time', 'horizon']) # Need to drop time axis and time horizon to allow next steps
                    abs_change = dat[metric] - ref # absolute delta is not precalculated for 1981-2010, so manually calc for both for consistency
                    percent_deltas = 100 * abs_change / ref # calculate percent change
                elif freq in ['MS', 'QS-DEC']: # for sub-annual indices
                    ref = unstack_time(ref).squeeze().drop_vars(['year', 'horizon']) # Apply unstack_time to replace time dim with 'year' and 'month' coords. Need to drop year axis and time horizon to allow next steps
                    abs_change = unstack_time(dat[metric]) - ref #  Apply stack_time to generate separate 'year' and 'month' dims. Absolute delta is not precalculated for 1981-2010, so manually calc for both for consistency
                    percent_deltas = 100 * abs_change / ref # calculate percent change
                    percent_deltas = restack_time(percent_deltas) # restack year and month dims into single time   
                
                # NOTE: there will be infinite values in the results (metric = any value where zero historically) 
                # Similarly, there will be NaNs where metric = zero historically and future, as well as in regions outside of the Canada domain
                
                # copy over variable attrs and update as necessary. Needs to be inside loop so ref_period attrs (e.g., delta_reference) are updated correctly
                if metric not in ['dlyfrzthw_tx0_tn-1', 'nr_cdd']:
                    percent_deltas.attrs['standard_name'] = dat[metric].attrs['standard_name'] # standard name not available for dlyfrzthw_tx0_tn-1 and nr_cdd
                percent_deltas.attrs['cell_methods'] = dat[metric].attrs['cell_methods'] + ' time: mean over years' # Fix cell methods, which were not updated when climo stats were taken originally
                ## LV NOTE: do we want to 'fix' cell methods to add climo stats? this will mean attrs are different than other M6 indices, unfortch
                percent_deltas.attrs['delta_kind'] = 'perc.'
                percent_deltas.attrs['units'] = '%'
                percent_deltas.attrs['delta_reference'] = horizon2[ref_period]
                percent_deltas.attrs['long_name'] = dat[metric].attrs['long_name'] + f": perc. delta compared to {horizon2[ref_period]}."
                percent_deltas.attrs['description'] = dat[metric].attrs['description'] + f": perc. delta compared to {horizon2[ref_period]}."
                if metric == 'snowfall_season_length': # no existing attr 'history' for this index
                    percent_deltas.attrs['history'] = f'[{datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}] perc. delta vs. 1971-2000 and 1981-2010 - xarray v{xr.__version__}'
                else: # append current calc to history attr
                    percent_deltas.attrs['history'] = f'[{datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}] perc. delta vs. 1971-2000 and 1981-2010 - xarray v{xr.__version__} \n ' \
                                                        + dat[metric].attrs['history'] 
                
                # rename variable and add to dictionary
                dct[ref_period] = percent_deltas.rename(f'{metric}_percent_delta_{horizon1[ref_period]}')
            
            # merge two reference period arrays to one dataset
            outdat = xr.merge(dct.values())
            for var in ['lat','lon','time']: # update index attrs
                outdat[var].attrs = dat[var].attrs
            
            # copy over file attrs
            outdat.attrs = dat.attrs
            
            # delete outdated attrs, these do not exist in snow variables
            try: del(outdat.attrs['cat:_data_format'], outdat.attrs['cat:path']) # LV: could leave for consistency sake, even though incorrect
            except KeyError: pass
            
            # set encoding 
            encoding = {var: {'dtype': 'float32',
                              'zlib': True, # compress outputs
                              'complevel': 5, # 1 to 9, where 1 is fastest, and 9 is maximum compression
                              '_FillValue': 1e+20, # missing value depreciated, not added
                              'chunksizes': [len(outdat.time), 30, 30]
                              } for var in outdat.data_vars} 
            
            # save
            outdat.to_netcdf(f'{outpath}/{metric}_{freq_label[freq]}_MBCn+PCIC-Blend_{mod}_historical+{ssp}_1950-2100_30ymean_percent_delta.nc', encoding=encoding)
        
            # free up memory
            del([dat, dct, ref, abs_change, percent_deltas, outdat])
            gc.collect()
            
print('All files complete!') 