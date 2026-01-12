# -*- coding: utf-8 -*-
"""
Author: Laura Van Vliet
Date: July 15, 2025 

Calculate ensemble percentiles for percentage change for all CanDCS-M6 with percentage change (those with base zero, excluding temperature value and day of year indices).

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
"""

import os
import glob
import xarray as xr
import gc
from xclim.ensembles import ensemble_percentiles
from filepaths import filepaths 

# Dictionary of scales for which metrics were calculated (annual, seasonal, monthly). Not all indices have subannual indices.
freq_dict = {#'cddcold_18': ['YS'],
             #'cdd': ['YS'],
             'dlyfrzthw_tx0_tn-1': ['YS'],
             'frost_days': ['YS'],
             'frost_free_season': ['YS'],
             'gddgrow_0': ['YS', 'MS'],
             'gddgrow_5': ['YS'],
             'hddheat_18': ['YS'],
             'ice_days': ['YS'],
             'nr_cdd': ['YS', 'MS'],
             'prcptot': ['YS', 'QS-DEC', 'MS'],
             'prsntot': ['YS', 'QS-DEC'], #, 'MS'], # MS commented out for snow metrics, as % change calcs failed due to file size/access issues
             'r10mm': ['YS', 'QS-DEC', 'MS'],
             'r1mm': ['YS', 'QS-DEC', 'MS'],
             'r20mm': ['YS', 'QS-DEC', 'MS'],
             'rx1day': ['YS', 'QS-DEC', 'MS'],
             'rx5day': ['YS', 'MS'],
             'sn10mm': ['YS', 'QS-DEC'], #, 'MS'],
             'sn2mm': ['YS', 'QS-DEC'], #, 'MS'],
             'snowfall_season_length': ['YS-JUL'], # YS-JUL is annual, where year starts in summer
             'snx1day': ['YS', 'QS-DEC'], #, 'MS'],
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

# dictionary of frequency labels used in filenames versus folder structure
freq_label = {'YS': 'ann',
              'QS-DEC': 'sea',
              'MS': 'mon',
              'YS-JUL': 'ann-juljun'}
   
ssps = ['ssp126', 'ssp245', 'ssp370', 'ssp585']    
    
# all available models for CMIP6 CanDCS-M6
models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'BCC-CSM2-MR', 'CMCC-ESM2', 'CNRM-CM6-1',
          'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-Veg', 'EC-Earth3', 'FGOALS-g3', 'GFDL-ESM4',
          'INM-CM4-8', 'INM-CM5-0', 'IPSL-CM6A-LR', 'KIOST-ESM',
          'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'NorESM2-LM', 
          'NorESM2-MM', 'TaiESM1', 'HadGEM3-GC31-LL', 'UKESM1-0-LL', 'KACE-1-0-G']

# function for open_mfdataset to allow ensemble creation over realization dimension
def add_model_dim(ds):
    flnm = ds.encoding['source'] # get filename (unique to each model) from dataset encoding
    # add realization as a dimension on the dataset, using flnm as realization name
    ds = ds.assign_coords(realization=flnm).expand_dims('realization')
    return ds

mask = xr.open_dataset(f'{filepaths.M6_outpath}/PCIC-Blend-mask.nc')['mask']

# Loop through models calculating percentage change and saving to netCDF
for metric, frequency_scales in freq_dict.items():

    print(f'.... {metric}')

    for ssp in ssps: 
        
        print(f'.............. {ssp}')
        
        for freq in frequency_scales:
        
            print(f'..................... {freq}')    
        
            # create directory for this metric, frequency, and ssp 
            outpath = f'{filepaths.M6_outpath}/{metric}/{freq}/{ssp}/ensemble_percentiles/'
            os.makedirs(outpath, exist_ok=True)
            
            inpath = f'{filepaths.M6_outpath}/{metric}/{freq}/{ssp}/simulations_30yAvg/' # input data location
            ens_files = glob.glob(f'{inpath}/{metric}_{freq_label[freq]}_MBCn+PCIC-Blend_*_historical+{ssp}_1950-2100_30ymean_percent_delta.nc')
        
            # rather than using xclim.ensembles, create ensemble manually with open_mfdataset and a preprocess to add the realization dimension.
            # open_mfdataset does not automatically pad with NaNs or align calendar, to better catch potential errors
            # it also has better handling of attrs (where xclim takes attrs from the first dataset)
            ensemble = xr.open_mfdataset(ens_files, decode_timedelta=False, # open data using decode_time = False so that count-based indices (units of days) are not converted to timedelta objects
                                         preprocess=add_model_dim, # preprocess adds model (called realization) as a dimension
                                         join='exact', # "raise ValueError when indexes to be aligned are not equal"
                                         combine_attrs="drop_conflicts" # "attrs from all objects are combined, any that have the same name but different values are dropped."
                                         ).chunk({'realization':-1}) # "-1" will create one large chunk along realization dim to allow for ens percentiles 
            # drop conflict above will also drop history attrs for variables, since timestamps are slighly different
            # add history attrs back in, using first file in list
            for var in ensemble.data_vars: 
                ensemble[var].attrs['history'] = xr.open_dataset(ens_files[0])[var].attrs['history']
                
            # check to make sure all files/model runs exist
            if ssp == 'ssp370': # two models don't have runs for ssp370
                assert len(ensemble.realization) == 24, f'There are only {len(ensemble.realization)} ensemble members, not 24'
            else:
                assert len(ensemble.realization) == 26, f'There are only {len(ensemble.realization)} ensemble members, not 26'
            
            # Check for NaNs in % change files. Zero divided by zero above will return NaN. (Number divided by zero = infinity, these are not changed)
            # Zeros exist in the historical period when a threshold is not met. Fill nans with zero to indicate no change
            # fillna will also fill in ocean areas, so apply mask to clip to Canada domain again   
            ensemble_fillna = ensemble.fillna(0).where(mask == 100) 
    
            ens_percentiles = ensemble_percentiles(ensemble_fillna, # call xclim ensemble percentiles func
                                                   min_members=None, # minimum number of valid ensemble members for a statistic to be valid. Setting to "None" set it to the size of realization dimension.
                                                   # Note: this should not be an issue since all NaNs have been filled with zeros above
                                                   values=[10, 50, 90], # percentiles to calculate
                                                   split=True, # split each percentile into a new variable
                                                   method='linear') # the default method for estimating percentile, adding here for clarity. 
            
            ## setting split=True above copies variable attrs to file attrs. Need to append history to var attrs
            for var in ens_percentiles.data_vars:
                ens_percentiles[var].attrs['history'] = ens_percentiles.attrs['history'] + ' /n' + ensemble[metric + '_percent_delta_1971_2000'].attrs['history']
            # then, manually delete var attrs from file attrs 
            for attr in ['cell_methods', 'delta_kind', 'units', 
                         'delta_reference', 'long_name', 'description', 'history']: 
                del(ens_percentiles.attrs[attr])  
            if metric not in ['dlyfrzthw_tx0_tn-1', 'nr_cdd']: # these two metrics do not have attr 'standard name'
                del(ens_percentiles.attrs['standard_name'])  
            
            # set encoding 
            encoding = {var: {'dtype': 'float32',
                              'zlib': True, # compress outputs
                              'complevel': 5, # 1 to 9, where 1 is fastest, and 9 is maximum compression
                              '_FillValue': 1e+20, # missing value depreciated, not added
                              'chunksizes': [len(ens_percentiles.time), 30, 30]
                              } for var in ens_percentiles.data_vars} 
            
            # save
            ens_percentiles.to_netcdf(f'{outpath}/{metric}_{freq_label[freq]}_MBCn+PCIC-Blend_historical+{ssp}_1950-2100_30ymean_percentiles_fillna.nc', 
                                      encoding=encoding)
        
            # free up memory
            del([ens_files, ensemble, ens_percentiles])
            gc.collect()

print('All ensemble percentiles calculated!')