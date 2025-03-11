# -*- coding: utf-8 -*-

import xarray as xr
from xclim.ensembles import ensemble_percentiles
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import shutil
import glob, os
from math import log10, floor

# list of rcps
# list of rcps
ssps = ['historical', 'rcp26', 'rcp45', 'rcp85']

#list of percentiles
percs = ['p50', 'p10', 'p90']

#read in file
idfnew = xr.open_dataset('C:/Users/pomeroyc/Downloads/national_IDF_projection_dataset_CMIP5_v3.nc').rename_dims(dims_dict={"model":"realization"})
idfhist = xr.open_dataset('C:/Users/pomeroyc/Downloads/idfhistv3.nc')

#ensemble
idfens = ensemble_percentiles(idfnew, values=(10, 50, 90))

#add station name back in
idfens = idfens.assign_coords({"station_name": ("station", idfnew['station_name'])}).fillna(-99.9)
idfhist = idfhist.assign_coords({"lon": ("station", idfhist['lon'])})
idfhist = idfhist.assign_coords({"lat": ("station", idfhist['lat'])})

#sig fig rounding




#outpath
fld = 'C:/Users/pomeroyc/Desktop/CCDP/IDF/v3_3/CMIP5/'

#for stn in list(idfens['station'].values):
for stn in  list(idfens['station'].values):
    print(stn)
    sname = str(idfens.sel(station = stn).station_name.values)
    if not os.path.isdir(fld+stn+'/'):
        os.mkdir(fld+stn+'/')
        outpath = fld+stn+'/'
        #add doc.txt file to outpath
        shutil.copyfile(fld+'ReadMe.pdf', outpath+'ReadMe.pdf')
        shutil.copyfile(fld+'LisezMoi.pdf', outpath+'LisezMoi.pdf')
    for r in ssps:
        if r == "historical":
            df_out = pd.DataFrame()
            df = pd.DataFrame()
            for rp in list(idfens['return_period'].values):
                dhist = idfhist.sel(station = stn, return_period = rp)['IDF_data']
                dhistcl = idfhist.sel(station = stn, return_period = rp)['IDF_confidence']
                tmp = [np.round(x,1) for x in dhist.values]
                tmp.extend([np.round(x,1) for x in dhistcl.values])
                df[rp] = tmp
                
            durations = list(idfens['duration'].values)
            durations.extend([x+"_95%_confidence_limit" for x in durations])
            df.insert(0, "Duration", durations, True)
            df_out = pd.concat([df_out, df])
            
        
            lon= str(np.round(dhist.lon.values, 2))
            lat= str(np.round(dhist.lat.values, 2))
            
            df_out.to_csv(outpath+sname+'_'+stn+'_'+lat+'_'+lon+'_'+'historical.csv', index=False)

        else:
            if not os.path.isdir(fld+stn+'/'+r):
                os.mkdir(fld+stn+'/'+r)
            #create outpath for writing each rcp 
            outpath_r = fld+stn+'/'+r+'/'
            #Only populate time periods after ref period - separately? Can I do this all at once?
            gen = (x for x in list(idfens['time'].values.astype('datetime64[Y]').astype(int)+1970) if x >= 2011)
            for ts in gen:
                df_out = pd.DataFrame()
                #convert t for subsetting
                t = str(ts)+'-01-01'
                df = pd.DataFrame()
                #add columns - one for each 
                for p in percs:
                    for rp in list(idfens['return_period'].values):
                        #select station
                        da = idfens.sel(station = stn, rcp = r, time = t, return_period = rp)['IDF_data_'+p]
                        dacl = idfens.sel(station = stn, rcp = r, time = t, return_period = rp)['IDF_confidence_'+p]
                        if p == 'p10':
                            pn = '10th_percentile'
                        if p == 'p50':
                            pn = 'median'
                        if p == 'p90':
                            pn = '90th_percentile'
                        """
                        #combine iteratively
                        daf = [x for y in zip(da.values, dacl.values) for x in y]
                        """
                        #tmp = [np.round(x,-1) for x in da.values]
                        tmp = [sigfig.round(x, sigfigs = 2) if len(str(np.round(x,1))) <= 4 else sigfig.round(x, sigfigs = 3) for x in da.values]
                        #tmp.extend([np.round(x,-1) for x in dacl.values])
                        tmp.extend([sigfig.round(x, sigfigs = 2) if len(str(np.round(x,1))) <= 4 else sigfig.round(x, sigfigs = 3) for x in dacl.values])
                        df[rp+'_'+pn] = tmp
     
                #add time period column
                #add list of durations to df as column
                durations = list(idfens['duration'].values)
                durations.extend([x+"_95%_confidence_limit" for x in durations])
                df.insert(0, "Duration", durations, True)
                df_out = pd.concat([df_out, df])
                
            
                #add ref period column
                #df_out.insert(1, "ref_period", idfnew.sel(station = stn)['ref'].values, True)
                lon= str(np.round(da.lon.values, 2))
                lat= str(np.round(da.lat.values, 2))
                sname= str(da.station_name.values)
                
                #overly complicated way to add "historical" to file name for historical file
                df_out.to_csv(outpath_r+sname+'_'+stn+'_'+lat+'_'+lon+'_'+r+'_'+str(ts)+'-'+str(int(ts)+29)+'.csv', index=False)
        
    #go to high level folder, select folders and doc.txt and zip them
    os.chdir(fld)        
    flst = next(os.walk('.'))[1]
    for dir_name in flst:
        shutil.make_archive(sname+'_'+stn+'_'+lat+'_'+lon+'_cmip5', 'zip', dir_name)
    shutil.rmtree(outpath)
            
        
    
    
    

#plot x = freq, y = intensity - maybe start with medians for one RCP (diff colors for each period and different lines for each rcp )
    