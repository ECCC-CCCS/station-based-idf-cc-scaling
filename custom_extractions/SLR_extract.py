#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 22:24:10 2025

@author: evg000
"""

def extract_SLC(ssp, sheet_names):
    import os
    import numpy as np
    import pandas as pd
    import xarray as xr
    import sys
    from functions import get_csv
    sys.path.append(os.path.expanduser('~/scratch/'))
    from filepaths import cspaths
    
    directory = cspaths.workspace
    rslc_dir = cspaths.rslc
    output_dir = f'{directory}/output/'
    i='rslc'
    perc = ['_p17','_p50','_p83']        
    
    #projection = "https://pavics.ouranos.ca/twitcher/ows/proxy/thredds/fileServer/birdhouse/disk2/cccs_portal/indices/Final/SEA_LEVEL_RISE/Decadal_CMIP6_ensemble-percentiles_allssps_2020-2150_rslc_YS_final.nc#mode=bytes"
    projection = f'{rslc_dir}/Decadal_CMIP6_ensemble-percentiles_allssps_2020-2150_rslc_uplift_YS.nc' #Decadal_CMIP6_ensemble-percentiles_allssps_2020-2150_rslc_YS.nc'
    
    #preprocess the climate data for coastal information
    ds = xr.open_dataset(projection)
    
    ds.load()
    
    for flnm in sheet_names:
        
        df = get_csv(flnm)
        df_ind = pd.DataFrame()
        
        for index,row in df.reset_index().iterrows():
            df_p = pd.DataFrame()
            for p in perc:
                #selects site
                
                ds_site = ds[ssp+'_'+i+p].sel(lon=row['Longitude'],lat=row['Latitude'],method='nearest').drop_vars(['lat','lon'])
                
                df_temp = ds_site.to_dataframe(row['FederalSiteIdentifier']).T
                #create a set of tuple for column names
                yrs = list(ds_site.time.dt.year.values.flatten())
                a = [list(np.repeat(i+p,len(yrs))), yrs]
                df_temp.columns = pd.MultiIndex.from_tuples(list(zip(*a)))
                df_temp.index.name='FederalSiteIdentifier'
                #append together data
                df_p = pd.concat([df_p,df_temp],axis=1)
                    
            new_order = [np.tile([i+p for p in perc], len(yrs)), list(np.repeat(yrs, 3))]
            df_p = df_p[pd.MultiIndex.from_tuples(list(zip(*new_order)))]

            df_ind = pd.concat([df_ind,df_p],axis=0)

        #add site names, lat, lon to the output
        df.columns = pd.MultiIndex.from_tuples(list(zip(*[df.columns, [""]*len(df.columns)]))) # have to turn df cols into multi-index for concat to work
        
        df_ind = pd.concat([df, df_ind],axis=1)

        input_name = os.path.basename(flnm).split('.csv')[0]
        df_ind.to_csv(f'{output_dir}SLR_{ssp}_{input_name}.csv')  
        
    ds.close()
