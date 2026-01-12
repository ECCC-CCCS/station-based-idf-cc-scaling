# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 16:17:47 2022

@author: VanVlietL, edited by @evagnegy
"""

def extract_GCM(GCM_variables, gcm_type, ssp, periods, sheet_names):
    
    import xarray as xr
    import pandas as pd
    import numpy as np
    import os
    from functions import get_csv,closest_node
    import sys
    sys.path.append(os.path.expanduser('~/scratch/'))
    from filepaths import cspaths
    
    directory = cspaths.workspace
    output_dir = f'{directory}/output/'
    
    pers = {'1981_2010': ('1981', '2010'),
            '2011_2040': ('2011', '2040'), 
            '2041_2070': ('2041', '2070'),
            '2071_2100': ('2071', '2100') 
            }
    
    precision = dict(siconc=2,
                     sithick=2, 
                     sfcWind=2,
                     snd=3,
                     dissic=2,
                     ph=2, 
                     talk=2,
                     sos=2,
                     tos=1)
    
    model_num = dict(siconc=23,
                     sithick=17, 
                     sfcWind=20,
                     snd=16,
                     dissic=10,
                     ph=8, 
                     talk=11,
                     sos=29,
                     tos=32)
    
    # index
    ar_t = np.array([])
    for vr in list(np.repeat(GCM_variables, len(periods))):
        for i in ['p10', 'p50', 'p90']:
            ar_t = np.append(ar_t, vr + '_' + i)
    ar_b = np.tile(np.repeat(periods, 3), len(GCM_variables))
            
    arrays = [list(ar_t),
              list(ar_b)]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=["variable", "period"])
    error_st = np.array([])
    

    

    for flnm in sheet_names:
        
        lst = get_csv(flnm)
        df = pd.DataFrame(index=lst.index, columns=index)
        
        for var in GCM_variables:
            
            if var == 'sfcWind' and ssp == 'ssp370':
                continue
            
            if gcm_type=='ocean' and ssp == 'ssp370':
                continue
            
            for qt in  ['0.1', '0.5', '0.9']:
                for p in pers:
                    
                    #fl = f'{pth}/GCM/{var}_{rcp}_{pers[p][0]}_{pers[p][1]}_{qt}_pctl_CMIP5_GCM.nc'
                    #path='https://hpfx.collab.science.gc.ca/~sccc001/sccc001/FCSAP_CMIP6/'
                    file=f'{var}_{ssp}_{pers[p][0]}_{pers[p][1]}_{qt}_pctl_CMIP6_{model_num[var]}GCM.nc'
                    
                    
                    dat = xr.open_dataset(f"{directory}/gcm_30yrs/{file}")[var]
                    
                                            
                    for st in lst.index:
                       
                        try:
                            xx, yy = 360 + lst.loc[st,'Longitude'], lst.loc[st,'Latitude'] # convert long from neg to pos
                            value = dat.sel(lat=yy, lon=xx, method="nearest").values
                            #if np.isnan(value) and gcm_type=='ocean':
                            #    value = closest_node(dat, xx, yy, radius=2)
                            #else: pass
                            df.loc[st, (f'{var}_p{qt[-1]}0', f'{pers[p][0]}_{pers[p][1]}')] = value
                        except (ValueError): error_st = np.append(error_st, st) # for no lat-lon cases 
            
                    df[f'{var}_p{qt[-1]}0'] = df[f'{var}_p{qt[-1]}0'].astype('float32').round(precision[var]) # convert to float, required to round
        
        #add site names, site lat, site lon to the output data table
        lst.columns = pd.MultiIndex.from_tuples(list(zip(*[lst.columns, [""]*len(lst.columns)]))) # have to turn df cols into multi-index for concat to work
        df = pd.concat([lst, df],axis=1)
        
        #save            
        input_name = os.path.basename(flnm).split('.csv')[0]
        df.to_csv(f'{output_dir}CMIP6_GCM_{gcm_type}_{ssp}_{input_name}.csv')                    



