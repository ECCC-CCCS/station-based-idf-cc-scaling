import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager
import matplotlib.patches as patches
import pandas as pd
import matplotlib as mpl
import scipy.stats as stats
import pickle as pickle
import threddsclient
import itertools
import os
import glob
import xarray
import time

start = time.time()

latitude=42.3149
longitude=-83.0364


vars=['tnlt_-15']
rcps=['rcp26','rcp45','rcp85']

mods=['BNU-ESM', 'CCSM4', 'CESM1-CAM5', 'CNRM-CM5', 'CSIRO-Mk3-6-0', 
            'CanESM2', 'FGOALS-g2', 'GFDL-CM3', 'GFDL-ESM2G','GFDL-ESM2M', 
            'HadGEM2-AO','HadGEM2-ES', 'IPSL-CM5A-LR', 'IPSL-CM5A-MR', 
            'MIROC-ESM-CHEM', 'MIROC-ESM', 'MIROC5', 'MPI-ESM-LR','MPI-ESM-MR',
            'MRI-CGCM3', 'NorESM1-M', 'NorESM1-ME', 'bcc-csm1-1-m', 'bcc-csm1-1']


portal="https://pavics.ouranos.ca/thredds/catalog/birdhouse/cccs_portal/indices/Final/BCCAQv2/"

output='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/05 - Personal/DeGroot/Decision Making Exercise/Output Data/Time Series/CD/-15/final/'


selected_var=[]

for var in vars: 
    for r in rcps:
        
        selected_var_a = [ds for ds in threddsclient.crawl(portal+var+"/YS/"+r+'/simulations/'+"catalog.html",depth=10) if 'r1i1p1' in ds.name]
        selected_var.append(selected_var_a)
selected_var_flat = list(itertools.chain(*selected_var))


selected_var_new=[]
for i in selected_var_flat:
    if 'HadGEM2-ES' not in i.name and 'HadGEM2-CC' not in i.name and 'inmcm4' not in i.name and 'ACCESS1-0' not in i.name: 
        selected_var_new.append(i)

##########RCP26###############

#selected_var_26=[]
# =============================================================================
# for j in selected_var_new:
#     if 'rcp26' in j.name:
#         selected_var_26.append(j)
# 
# n1=len(selected_var_26)
# 
# list_26=[]
# =============================================================================
# =============================================================================
# for n1 in range(0,n1):
#     r=selected_var_26[n1]
#     r=str(r.opendap_url())
#     ds26=xarray.open_dataset(r,decode_times=False)
#     ds26['time'] = xarray.decode_cf(ds26).time
#     dataSel_26 = ds26[var].sel(lat=latitude, lon=longitude, method='nearest')
#     YYstring=pd.Series(ds26['time.year'].values)
#     values26=dataSel_26.values
#     values26=values26.reshape(151,)
#     values26=pd.Series(values26)
#     table26 = pd.concat([values26], axis=1)
#     table26.columns=['m1']
#     table26.index = YYstring
#     
#     
# ########NEW PERCENTILE CODE 26##################
# 
# years=np.arange(1950,2100,1)
# percentile=(5, 25, 50, 75, 95)
# 
# list_rcp26=[]
# for r in years:
#     for p in percentile:
#         list_rcp26.append([r, p, np.percentile(table26.loc[r], p)])
# 
# table_rcp26=pd.DataFrame(list_rcp26,columns=['years','percentile','value'])
# table_rcp26=table_rcp26.pivot(index='years', columns='percentile', values='value')
# table_rcp26=table_rcp26.loc['years','25','50','75']
# table_rcp26=table_rcp26.loc[: ,[25,50,75]]
# QQ_rcp26=table_rcp26
# 
# 
# rcp26_25=QQ_rcp26[25].values
# rcp26_50=QQ_rcp26[50].values
# rcp26_75=QQ_rcp26[75].values
# =============================================================================

# =============================================================================
# frame_1=pd.concat(list_rcp26, axis=1)
# frame_1=frame_1.T
# frame_1.columns=['p25','p50','p75']
# frame_1.index=table26.index
# QQ_rcp26=frame_1
# # 
# =============================================================================

##########################################    
    
    
# =============================================================================
#     list_26.append(table26)
# frame26 = pd.concat(list_26, axis=1)
#     
# 
# list_1_26=[]
# for year in frame26.index:
#     QQ26=stats.mstats.mquantiles(frame26.loc[year],prob=[0.25, 0.5, 0.75],alphap=0.5,betap=0.5)
#     QQ26=pd.DataFrame(QQ26)
#     QQ26_table= pd.DataFrame(QQ26)
#     QQ26_table= pd.concat([QQ26], axis=1)
#     list_1_26.append(QQ26_table)
# frame_1=pd.concat(list_1_26, axis=1)
# frame_1=frame_1.T
# frame_1.columns=['p25','p50','p75']
# frame_1.index=frame26.index
# QQ_rcp26=frame_1
# 
# =============================================================================


##########RCP45###############

# =============================================================================
# selected_var_45=[]
# for j in selected_var_new:
#     if 'rcp45' in j.name:
#         selected_var_45.append(j)
#          
# 
# n2=len(selected_var_45)
# 
# list_45=[]
# for n2 in range(0,n2):
#     r=selected_var_45[n2]
#     r=str(r.opendap_url())
#     ds45=xarray.open_dataset(r,decode_times=False)
#     ds45['time'] = xarray.decode_cf(ds45).time
#     dataSel_45 = ds45[var].sel(lat=latitude, lon=longitude, method='nearest')
#     YYstring=pd.Series(ds45['time.year'].values)
#     values45=dataSel_45.values
#     values45=values45.reshape(151,)
#     values45=pd.Series(values45)
#     table45 = pd.concat([values45], axis=1)
#     table45.columns=['m1']
#     table45.index = YYstring
#     list_45.append(table45)
# frame45 = pd.concat(list_45, axis=1)
#     
# 
# list_1_45=[]
# for year in frame45.index:
#     QQ45=stats.mstats.mquantiles(frame45.loc[year],prob=[0.25, 0.5, 0.75],alphap=0.5,betap=0.5)
#     QQ45=pd.DataFrame(QQ45)
#     QQ45_table= pd.DataFrame(QQ45)
#     QQ45_table= pd.concat([QQ45], axis=1)
#     list_1_45.append(QQ45_table)
# frame_2=pd.concat(list_1_45, axis=1)
# frame_2=frame_2.T
# frame_2.columns=['p25','p50','p75']
# frame_2.index=frame45.index
# QQ_rcp45=frame_2
# 
# 
# rcp45_25=QQ_rcp45['p25'].values
# rcp45_50=QQ_rcp45['p50'].values
# rcp45_75=QQ_rcp45['p75'].values
# =============================================================================

##########RCP85###############
        
selected_var_85=[]
for l in selected_var_new:
    if 'rcp85' in l.name:
        selected_var_85.append(l)

n2=len(selected_var_85)

list_85=[]
for n2 in range(0,n2):
    r=selected_var_85[n2]
    r=str(r.opendap_url())
    ds85=xarray.open_dataset(r ,decode_times=False)
    ds85['time'] = xarray.decode_cf(ds85).time
    dataSel = ds85[var].sel(lat=latitude, lon=longitude, method='nearest')
    YYstring=pd.Series(ds85['time.year'].values)
    values85=dataSel.values
    values85=values85.reshape(151,)
    values85=pd.Series(values85)
    table85 = pd.concat([values85], axis=1)
    table85.columns=['m1']
    table85.index = YYstring
    list_85.append(table85)
frame85 = pd.concat(list_85, axis=1)

#############DATA UP TO HERE IS GOOD########################

list_1_85=[]
for year in frame85.index:
    QQ85=stats.mstats.mquantiles(frame85.loc[year],prob=[0.25, 0.50, 0.75],alphap=0.5,betap=0.5)
    QQ85=pd.DataFrame(QQ85)
    QQ85_table= pd.DataFrame(QQ85)
    QQ85_table= pd.concat([QQ85], axis=1)
    list_1_85.append(QQ85_table)
frame_3=pd.concat(list_1_85, axis=1)
frame_3=frame_3.T
frame_3.columns=['p25','p50','p75']
frame_3.index=frame85.index
QQ_rcp85=frame_3

rcp85_25=QQ_rcp85['p25'].values
rcp85_50=QQ_rcp85['p50'].values
rcp85_75=QQ_rcp85['p75'].values

#####################################
# =============================================================================
# rcp26_25=QQ_rcp26['p25'].values
# rcp26_50=QQ_rcp26['p50'].values
# rcp26_75=QQ_rcp26['p75'].values
# 
# rcp45_25=QQ_rcp45['p25'].values
# rcp45_50=QQ_rcp45['p50'].values
# rcp45_75=QQ_rcp45['p75'].values
# 
# rcp85_25=QQ_rcp85['p25'].values
# rcp85_50=QQ_rcp85['p50'].values
# rcp85_75=QQ_rcp85['p75'].values
# =============================================================================
