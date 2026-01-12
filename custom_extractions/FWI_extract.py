#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 22:25:09 2025

@author: evg000
"""

def extract_FWI(indices, rcp, periods, sheet_names):
    import os
    import numpy as np
    import pandas as pd
    import xarray as xr
    import sys
    from functions import get_csv, closest_node
    sys.path.append(os.path.expanduser('~/scratch/'))
    from filepaths import cspaths
    
    directory = cspaths.workspace
    output_dir = f'{directory}/output/'
    
    fwi_dir = cspaths.fwi
    
    perc = ['quantile:0.1','quantile:0.5', 'quantile:0.9']
    perc_new = ['p10','p50', 'p90']
        
    rcps_fwi = {'RCP26': 'constructed_RCP26',  
                'RCP45': 'constructed_RCP45',  
                'RCP85': 'RCP85'}
            
    periods = [p.replace('_','-') for p in periods]        
    
    for flnm in sheet_names:   
        
      for val_typ in ['percent_delta_1971_2000_', '']:

          df = get_csv(flnm)
          df_ind=pd.DataFrame() 
                    
          for i in indices:
              
              if i == 'fire_season_length':
                  projection = f"{fwi_dir}{rcps_fwi[rcp]}/ensemble_percentiles/fire_season_length_{rcps_fwi[rcp]}_30yr_mean_{val_typ}ensemble_percentiles.nc"
                  ds = xr.open_dataset(projection, decode_timedelta=False)['fire_season']
                  ds = ds.drop_vars(["warming_level"])
              if i == 'FWIp95':
                  projection = f"{fwi_dir}{rcps_fwi[rcp]}/ensemble_percentiles/MJJAS_quantile_fillna_{rcps_fwi[rcp]}_30yr_mean_{val_typ}ensemble_percentiles.nc"
                  ds = xr.open_dataset(projection).sel(annual_quantiles=0.95)['FWI']
                  ds = ds.drop_vars(["annual_quantiles","warming_level"])
              if i == 'BUIp95':
                  projection = f"{fwi_dir}{rcps_fwi[rcp]}/ensemble_percentiles/MJJAS_quantile_fillna_{rcps_fwi[rcp]}_30yr_mean_{val_typ}ensemble_percentiles.nc"
                  ds = xr.open_dataset(projection).sel(annual_quantiles=0.95)['BUI']
                  ds = ds.drop_vars(["annual_quantiles","warming_level"])
         
              ds = ds.sel(period=periods, ensemble_statistic=perc).load() ## IMPORT TO LOAD. If you don't will re-open file for every station, very slow
              ds['ensemble_statistic'] = [f'p{nm.split(".")[-1]}0' for nm in ds.ensemble_statistic.values]              
              
              #blank dataframe for output for all sites, all vars, all percentiles
              df_sites = pd.DataFrame()
              for index,row in df.reset_index().iterrows():
                 
                  #selects site
                  ds_site = ds.sel(lon=row['Longitude'],lat=row['Latitude'],method='nearest').drop_vars(['lat','lon'])
                  # removed selected nearest gridcell if all NaNs > this data is masked for a reason in Northern Canada

                  df_p = ds_site.to_dataframe(row['FederalSiteIdentifier']).T
                  df_p.columns = df_p.columns.set_levels([f"{i}_{col_name}" for col_name in df_p.columns.levels[0] ], # add indices to col names
                                                         level=0)
                  df_p.index.name='FederalSiteIdentifier'
                                        
                  new_order =  [np.tile([f"{i}_{p}" for p in perc_new], len(periods)), list(np.repeat(periods, 3))]
                  df_p = df_p[pd.MultiIndex.from_tuples(list(zip(*new_order)))]
      
                  df_sites = pd.concat([df_sites,df_p],axis=0)
                  
              df_ind = pd.concat([df_ind,df_sites],axis=1)
              ds.close()
              
          #add site names, lat, lon to the output
          df.columns = pd.MultiIndex.from_tuples(list(zip(*[df.columns, [""]*len(df.columns)]))) # have to turn df cols into multi-index for concat to work
          
          df_ind = pd.concat([df, df_ind],axis=1) 
  
          input_name = os.path.basename(flnm).split('.csv')[0]
          df_ind.to_csv(f'{output_dir}FWI_{rcp}_{val_typ}{input_name}.csv')                 