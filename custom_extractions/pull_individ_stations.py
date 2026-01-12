# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 09:47:49 2025

@author: VanVlietL
"""

import os
import pandas as pd
import sys
import numpy as np
from datetime import datetime
sys.path.append(os.path.expanduser('~/scratch/'))
from filepaths import cspaths

input_dir = f'{cspaths.workspace}/output/'
output_dir = f'{cspaths.workspace}/output/stations/'

ssps = ['ssp126', 'ssp245', 'ssp370', 'ssp585']   
rcps = ['RCP26', 'RCP45', 'RCP85', 'RCP85'] # since we zip scenarios later for looping, need to have same length lists. RCP85 will be overwritten 
sheet_name = 'FCSAP_template_Jul23.csv'

datestring = datetime.now().strftime("%Y%m%d")

# function to convert column index into new multi-index with format: variable, percentile, period, scenario (each is a new level)
def split_col_index(df, scenario, append_percent=False):
    '''
    

    Parameters
    ----------
    df : Dataframe
        Dataframe with column index in two levels of format: (variable_percentile, period)
    scenario : String
        SSP or RCP. Will be added as new level on multi-index.
    append_percent : Boolean, optional
        If True, "_percentage_change" will be appended to the variable name in the new multi-index.
        This will differentiate it from absolute values with the same variable name. The default is False.

    Returns
    -------
    df : Dataframe
        Dataframe with new 4-level multi-index with format: variable, percentile, period, scenario (each is a new level)

    '''
    if append_percent:
        var = [i[0].split('_p')[0] + '_percent_change' for i in df.columns]
    else:
        var = [i[0].split('_p')[0] for i in df.columns]
    perct = ['p' + i[0].split('_p')[1] for i in df.columns]
    per = [i[1].replace('-', "_") for i in df.columns] # for FWI vars only will, reformat period labels 
    scen = np.repeat(scenario, len(var))
    new_index = pd.MultiIndex.from_tuples(list(zip(var, perct, per, scen)), 
                                          names=['variable','percentile','period', 'scenario'])
    df.columns = new_index      
    return df

# function to pull data for one station from dataframe, and then pivot so that "variable" is now the index
def pivot_station(full_frame, st):
    df = full_frame.loc[st].reset_index()
    out = df.pivot_table(values=st, index='variable', columns=['period','percentile','scenario'], dropna=False, aggfunc='first')
    return out

alldata = {}

for ssp, rcp in zip(ssps, rcps):
    
    # create dictionaries to hold all files, allow loop through
    ssp_dct = {}
    rcp_dct = {}
    
    # open csvs by data source
    ssp_dct['gcm_ocean'] = pd.read_csv(f'{input_dir}CMIP6_GCM_ocean_{ssp}_{sheet_name}', header=[0,1,2], index_col=0).iloc[:,14:]
    ssp_dct['gcm_atmos'] = pd.read_csv(f'{input_dir}CMIP6_GCM_atmos_{ssp}_{sheet_name}', header=[0,1,2], index_col=0).iloc[:,14:]
    ssp_dct['slr'] = pd.read_csv(f'{input_dir}SLR_{ssp}_{sheet_name}', header=[0,1,2], index_col=0).iloc[:,14:]
    ssp_dct['drought'] = pd.read_csv(f'{input_dir}GCM_drought_indices_{ssp}_{sheet_name}', header=[0,1,2], index_col=0).iloc[:,14:]
    ssp_dct['cdca'] = pd.read_csv(f'{input_dir}ClimateData_projections_{ssp}_{sheet_name}', header=[0,1,2], index_col=0).iloc[:,14:]
    ssp_dct['cdca_per'] = pd.read_csv(f'{input_dir}ClimateData_projections_percent_change_{ssp}_{sheet_name}', header=[0,1,2], index_col=0).iloc[:,14:] # CD.ca percentage change
   
    rcp_dct['fwi'] = pd.read_csv(f'{input_dir}FWI_{rcp}_{sheet_name}', header=[0,1,2], index_col=0).iloc[:,14:] 
    rcp_dct['fwi_per'] = pd.read_csv(f'{input_dir}FWI_{rcp}_percent_delta_1971_2000_{sheet_name}', header=[0,1,2], index_col=0).iloc[:,14:] # FWI percentage change
    
    # Loop through all dataframes, converting the column names currently in multi-index w format (variable_percentile, period) into new
    # multi-index with format: variable, percentile, period, scenario (each is a new level)
    for key, dataframe in ssp_dct.items():
        if key == 'cdca_per': # need to change variable names so they're not the same as for absolute values
            ssp_dct[key] = split_col_index(dataframe, ssp, append_percent=True)
        else:
            ssp_dct[key] = split_col_index(dataframe, ssp, append_percent=False)
    for key, dataframe in rcp_dct.items():
        if key == 'fwi_per': # need to change variable names so they're not the same as for absolute values
            rcp_dct[key] = split_col_index(dataframe, rcp, append_percent=True)
        else:
            rcp_dct[key] = split_col_index(dataframe, rcp, append_percent=False)
        
    alldata[ssp] = ssp_dct
    alldata[rcp] = rcp_dct
            
    del([ssp_dct, rcp_dct])
    
for station in alldata[ssp]['cdca'].index: # for station in station list
    
    # create new dictionary to hold data for single station
    station_dct = {}
    
    # loop through SSP/RCP dictionaries
    for ssp, rcp in zip(ssps, rcps):
        # get data for a single station from each dataframe, pivot so variable is now the index, and concat with other datasets w RCPs or SSPs
        station_dct[ssp] = pd.concat([pivot_station(df, station) for df in alldata[ssp].values()])
        station_dct[rcp] = pd.concat([pivot_station(df, station) for df in alldata[rcp].values()])
        
    # concat all reformatted data into one dataframe
    out = pd.concat(station_dct.values(), axis=1) 
    
    out.to_csv(f'{output_dir}{station}_{datestring}.csv') # save with date, so we can version control if needed


print('Complete!')