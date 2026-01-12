#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 14:33:56 2021

@author: ***REMOVED***
"""

import os
import xarray as xr
import pandas as pd
import openpyxl
from openpyxl import load_workbook

#%%

headdir = "/***REMOVED***/projects/custom-extractions/FAO/Data/Annual+30y_averages/ON+Sub-ER/"
xlsxpath = "/***REMOVED***/projects/custom-extractions/FAO/Data/ON-FAO_Climate-Indices_final.xlsx"

rcps = ['rcp26','rcp45','rcp85']
indices=['tg_mean', 'prcptot', 'rx5day', 'cddcold_18', 'txgt_30', 'txgt_32', 'tx_max','ftc_mild', 'ftc_deep', 'tx_mean', 'tasmax']
regions=['Northeast C', 'Northwest A','Northwest C', 'Northwest B', 'Ottawa', 'Kingston--Pembroke',
         'Muskoka--Kawarthas', 'Toronto', 'Kitchener--Waterloo--Barrie', 'Hamilton--Niagara Peninsula',
         'London', 'Windsor--Sarnia', 'Stratford--Bruce Peninsula', 'Northeast A', 'Northeast B', 'Ontario']
percentiles=['p50'] #, 'p10', 'p90']
freq = ["", "_30yAvgs"] #identifiers in file names to differentiate between

#%%

book = load_workbook(xlsxpath)
writer = pd.ExcelWriter(xlsxpath, engine = 'openpyxl')
writer.book = book


for r in rcps:
    for i in indices:
        workdir = headdir+r+'/'+i+'/'
        dirlist = os.listdir(workdir)
        
        for p in percentiles:
            for f in freq:
                df = pd.DataFrame()
                for reg in regions: #alternative for this loop could be something like "file_list = [ds for ds in dirlist if "30yavg" in ds]"
                    if f == "":
                        f2 = "YS"
                        ds = xr.open_dataset(workdir+reg+'_BCCAQv2_ensemble-percentiles_historical+'+r+'_1950-2100_'+i+'.nc')
                    else:
                        f2 = "30yAvgs"
                        ds = xr.open_dataset(workdir+reg+'_30yAvgs_BCCAQv2_ensemble-percentiles_historical+'+r+'_1976-2071_'+i+'.nc')                        
                    df_temp = ds[i+'_'+p].to_dataframe(reg).T
                    df = pd.concat([df,df_temp])
                    df.to_excel(writer, sheet_name = "_".join((r,i,p,f2)))               
writer.save()
writer.close()                
                
                
                
                
                
                
                
                
                
                