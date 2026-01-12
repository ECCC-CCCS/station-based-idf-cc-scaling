# -*- coding: utf-8 -*-
"""
Must be run on GPSC, data is not available on PAVICS. 
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
import sys
from functions import get_csv, closest_node
from filepaths import cspaths

directory = cspaths.workspace
output_dir = f'{directory}/output/'

def extract_CDca_percent(indices, ssp, periods, sheet_names):
    perc = ['_p10','_p50','_p90']
        
    freq_code = {
    "YS": "ann",
    "YS-JUL": "ann-juljun",  
    "MS": "mon",  
    "DS": "day"   
    }
    
    for flnm in sheet_names:
        
        df = get_csv(flnm)
        
        #blank dataframe for output for all sites, all vars, all percentiles
        df_ind=pd.DataFrame() 
                
        for i in indices:
        
            print(i)
                           
            if i == 'snowfall_season_length':
                frequency = "YS-JUL" #YS for annual, MS for monthly, DS for daily. Change to MS for July averaged tmax
            else: 
                frequency = 'YS'
                
            projection =  cspaths.M6_outpath +i+"/"+frequency+"/"+ssp+"/ensemble_percentiles/"\
                           +i+"_"+freq_code[frequency]+"_MBCn+PCIC-Blend_historical+"+ssp+"_1950-2100_30ymean_percentiles_fillna.nc"
            
            ds = xr.open_dataset(projection) 
                
            vlist=list(ds.data_vars.keys())
            
            for v in vlist:
                if '1971_2000' in v:
                    ds = ds.drop_vars(v) # drop 1971-2000 reference period deltas. We are only interested in 1981-2010 deltas
            
            ds = ds.sel(time=[f'{yr[:4]}' for yr in periods], method='nearest').load() ## IMPORT TO LOAD. If you don't will re-open file for every station, very slow. Method=nearest because snowfall season length has dates in July        

            #blank dataframe for all sites, all var, all percentiles
            df_sites = pd.DataFrame()
            for index,row in df.reset_index().iterrows():
                df_p = pd.DataFrame() # blank dataframe for all sites, 1 var, all percentiles
                for p in perc:
                    #selects site

                    ds_site = ds[f'{i}_percent_delta_1981_2010{p}'].sel(lon=row['Longitude'],lat=row['Latitude'],method='nearest').drop_vars(['lat','lon'])
                    #Check if the grid is missing data AND not because coordinates are missing in the input list
                    if np.all(np.isnan(ds_site.values.flatten())) and not np.isnan(row['Longitude']) and not np.isnan(row['Latitude']):
                        #if so, find next nearest grid for data
                        ds_site=closest_node(ds[f'{i}_percent_delta_1981_2010{p}'],row['Longitude'],row['Latitude'])

                    df_temp = ds_site.to_dataframe(row['FederalSiteIdentifier']).T # dataframe for one variable, one percentile, all periods
                    # modify the column headings
                    a = [list(np.repeat(i+p,len(periods))), periods]
                    df_temp.columns = pd.MultiIndex.from_tuples(list(zip(*a)))
                    df_temp.index.name='FederalSiteIdentifier'
                    #append together data for all percentiles for this var
                    df_p = pd.concat([df_p,df_temp.drop('horizon')],axis=1)
                
                    
                # re-organize column ordering
                new_order =  [np.tile([i+p for p in perc], len(periods)), list(np.repeat(periods, 3))]
                df_p = df_p[pd.MultiIndex.from_tuples(list(zip(*new_order)))]
                # concat site to dataframe
                df_sites = pd.concat([df_sites,df_p],axis=0)
            # concat all indicator data to dataframe
            df_ind=pd.concat([df_ind,df_sites],axis=1)
            #df_ind = df_ind.round(1) # round to 1 decimal
            ds.close()
        #add site names, site lat, site lon to the output data table
        df.columns = pd.MultiIndex.from_tuples(list(zip(*[df.columns, df.columns]))) # have to turn df cols into multi-index for concat to work
        df_ind = pd.concat([df, df_ind],axis=1)
        #df_ind = df_ind.round(1) # round to 1 decimal
        input_name = os.path.basename(flnm).split('.csv')[0]
        df_ind.to_csv(f'{output_dir}ClimateData_projections_percent_change_{ssp}_{input_name}.csv')         
