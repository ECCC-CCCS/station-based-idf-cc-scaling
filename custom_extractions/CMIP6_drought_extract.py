#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 22:24:42 2025

Interpretation of SPEI (and other standardized indices like SRI and SSI):

The Standardized Precipitation Evapotranspiration Index (SPEI) measures the difference between precipitation and 
potential evapotranspiration and provides that difference in number of standard deviations from the average in 
the reference period (1950-2005). Negative values indicate water deficit relative to 1950-2005 conditions, positive 
values indicate a water surplus relative to 1950-2005 conditions. An SPEI value of zero indicates no change relative to the historical conditions.		

SPEI therefore measures the difference between precipitation and potential evapotranspiration, i.e, the water loss from evaporation and vegetation. 
Therefore, "wetter" or "drier" in this context refers to more or less surface water availability (precipitation minus evapotranspiration).					
Note: Potential evapotranspiration refers to the evapotranspiration that would occur if sufficient water sources 
were available, that is, if water is not limiting.				

Technical note: SPEI is provided in units standard deviations from the reference period mean. There reference period for the CMIP6 dataset is 1950-2014.
Using a normal cumulative distribution function, we convert the standard deviations from the SPEI dataset to the probability that summers
with similar or less surface water availability to the average future summer would have occurred in the past. 

Ex 1: if standard deviation from ref period mean = 0. Converts to a probability value of 0.5 -> means the average future summer will be similar to the average historical summer. 
        Another way to say this is wetter than 50% of past summers.
Ex 2: if standard deviation from ref period mean = 0.5. Converts to a probability value of ~0.7 -> means the average future summer will be wetter than 70% of past summers. 
Ex 3: if standard deviation from ref period mean = -1. Converts to a probability value of ~0.15 -> means the average future summer will be wetter than 15% of past summers. 
        Another way to say this is drier than 85% of past summers.

A probability value of 0 means the average future summer will be drier than all historical summers, and 
A probability value of 1 means the average future summer will be wetter than all historical summers. 

Technical dataset notes: https://climate-scenarios.canada.ca/?page=cmip6-drought-notes
"""


def extract_drought(ssp, periods, sheet_names, drought_indices):
    import os
    import numpy as np
    import pandas as pd
    import xarray as xr
    import sys
    from scipy import stats
    from functions import get_csv, closest_node
    sys.path.append(os.path.expanduser('~/scratch/'))
    from filepaths import cspaths
    
    output_dir = f'{cspaths.workspace}/output/'
    spei_dir = f'{cspaths.workspace}CMIP6_drought/'
    
    perc = ['_p10','_p50','_p90']        
       
    mon_sel = {"_scale12": "12",  
               "_scale3": "8",
               "_YS": '1'  
               }
    label_dct = {"_scale12": "_12MS",  
                 "_scale3": "_3MS",
                 "_YS": ''  
                 }
    
    scales = ['_scale3', '_scale12']
    dummy_scales = ['_YS']
    
    scale_dict = {'SRI_surface': scales,
                  'SRI_total': scales,
                  'SSI_surface': scales,
                  'SSI_total': scales, 
                  'SPEI': scales,
                  'mrro': dummy_scales,
                  'mrros': dummy_scales,
                  'mrso': dummy_scales,
                  'mrsos': dummy_scales 
                  }
            
    def get_cdf(sd):
        '''
        The CDF is the probability that a random variable following a Student's t-distribution
        will take on a value less than or equal to a given x.
        
        Using a normal cumulative distribution function, convert the standard deviations provided by the 
        SPEI dataset to the probability that summers with similar or less surface water availability
        to the average future summer would have occurred in the past. 
        
        Parameters
        ----------
        sd : float
            Standard deviations from the reference period mean.
            
        Returns
        -------
        float
            Probability that summers with similar or less surface water availability
            to the average future summer would have occurred in the past.
        '''
        return stats.norm.cdf(sd).round(3) 
    
    for flnm in sheet_names:   
        
        df = get_csv(flnm)
        df_ind=pd.DataFrame() 
        
        for i in drought_indices:
        
            for scale in scale_dict[i]:
            
                projection = f"{spei_dir}/{i}{scale}_historical+{ssp}_1950-2100_30ymean_percentiles.nc"
                    
                ds = xr.open_dataset(projection)
                ds.load()
                
                ds = ds.sel(time=[f'{yr[:4]}-{mon_sel[scale]}-01' for yr in periods]).load() ## IMPORT TO LOAD. If you don't will re-open file for every station, very slow
            
                ds['lon'] = ds['lon']-360
            
                #blank dataframe for output for all sites, all vars, all percentiles
                df_sites = pd.DataFrame()
                for index,row in df.reset_index().iterrows():
                    df_p = pd.DataFrame() # blank dataframe for all sites, 1 var, all percentiles
                    for p in perc:
                        #selects site
                        ds_site = ds[f'{i.lower()}{p}'].sel(lon=row['Longitude'],lat=row['Latitude'],method='nearest').drop_vars(['lat','lon'])
                        
                        # LV: I have removed find nearest for NaN returns. CMIP5 excluded a lot of boundary/coastal areas, but this has been fixed in CMIP6. SPEI is on a 1x1 degree grid
                        ds_site = ds_site.where(ds_site < 9.96921e+36) # For some variables, the fill value is 9.9e36, replace these with NaNs otherwise get_cdf will return "1" (100% probabilty) in next line                                                     
                        df_temp = ds_site.to_dataframe(row['FederalSiteIdentifier']).T # covert to dataframe
                        if i in ['SRI_surface','SRI_total','SSI_surface','SSI_total','SPEI']:
                            df_temp = df_temp.map(get_cdf) # apply the function get_cdf to convert SD to probability 
                        
                        #create a set of tuple for column names
                        a = [list(np.repeat(f'{i}{label_dct[scale]}{p}',len(periods))), periods]
                        df_temp.columns = pd.MultiIndex.from_tuples(list(zip(*a)))
                        df_temp.index.name='FederalSiteIdentifier'
                     
                        #append together data
                        df_p = pd.concat([df_p,df_temp],axis=1)
        
                    new_order = [np.tile([f'{i}{label_dct[scale]}{p}' for p in perc], len(periods)), list(np.repeat(periods, 3))]
                    df_p = df_p[pd.MultiIndex.from_tuples(list(zip(*new_order)))]
        
                    df_sites = pd.concat([df_sites,df_p],axis=0)
                    
                df_ind = pd.concat([df_ind,df_sites],axis=1)
                ds.close()
            
        #add site names, lat, lon to the output
        df.columns = pd.MultiIndex.from_tuples(list(zip(*[df.columns, df.columns]))) # have to turn df cols into multi-index for concat to work
        
        df_ind = pd.concat([df, df_ind],axis=1) 

        input_name = os.path.basename(flnm).split('.csv')[0]
        df_ind.to_csv(f'{output_dir}GCM_drought_indices_{ssp}_{input_name}.csv')                    

