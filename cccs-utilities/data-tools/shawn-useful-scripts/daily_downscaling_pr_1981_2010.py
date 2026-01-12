import xarray
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import sys
import time
np.set_printoptions(threshold=sys.maxsize)

start= time.time()

input='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/03 - Data, Code & Models/01 - Data/downscaling/point_data/'

output='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/05 - Personal/Smith/Statistical Downscaling of Climate Models Research/Python Output/Trend Outputs/Annotations/'

fld1='pr_CanESM2_daily_1981to2010_raw.nc'
fld2='pr_CanESM2_daily_1981to2010_biasCorrected.nc'
fld3='pr_CanESM2_daily_1981to2010_qm_mmday.nc'
fld4='pr_CanESM2_daily_1981to2010_BCCAQ2.nc'
fld5='pr_anusplin_daily_1981to2010_anusplin.nc'


fh1 = xarray.open_dataset(input+fld1)
fh2 = xarray.open_dataset(input+fld2)
fh3 = xarray.open_dataset(input+fld3)
fh4 = xarray.open_dataset(input+fld4)
fh5 = xarray.open_dataset(input+fld5)


# use this for ALL time plotting on X axis
# must fix issues with leap years using different calendars
t=pd.date_range('1981-01-01 12:00:00','2010-12-24 12:00:00', freq='D')


# input arrays have different lengths. possibly leap years again. # likely NOT the best way to deal with this
time1 = (fh1['time'].values).flatten()
var1 = (fh1['pr'].values).flatten()
var1=var1[:10950]

time2 = (fh2['time'].values).flatten()
var2 = (fh2['pr'].values).flatten()

time3 = (fh3['time'].values).flatten()
var3 = (fh3['pr'].values).flatten()

time4 = (fh4['time'].values).flatten()
var4 = (fh4['pr'].values).flatten()

time5 = (fh5['time'].values).flatten()
var5 = (fh5['pr'].values).flatten()
var5=var5[:10950]

# linear regression code:

#raw
mx1=t
my1=var1
delta1 = (mx1 - mx1[0])
days1 = delta1.days
slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(days1,my1)
line1 = slope1*days1+intercept1 

#mean bias corrected
rx1=t
ry1=var2
delta2 = (rx1 - rx1[0])
days2 = delta2.days
slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(days2,ry1)
line2 = slope2*days2+intercept2  

#quantile mapping
sx1=t
sy1=var3
delta3 = (sx1 - sx1[0])
days3 = delta3.days
slope3, intercept3, r_value3, p_value3, std_err3 = stats.linregress(days3,sy1)
line3 = slope3*days3+intercept3

#bccaqv2
tx1=t
ty1=var4
delta4 = (tx1 - tx1[0])
days4 = delta4.days
slope4, intercept4, r_value4, p_value4, std_err4 = stats.linregress(days4,ty1)
line4 = slope4*days4+intercept4

#observations
ox5=t
oy5=var5
delta5 = (ox5 - ox5[0])
days5 = delta5.days
slope5, intercept5, r_value5, p_value5, std_err5 = stats.linregress(days5,oy5)
line5 = slope5*days5+intercept5 


# plotting now
fig, ax = plt.subplots(figsize=(12,10))

font_size1 = 24
font_size2 = 18
ax.set_title('Statistical Downscaling Methods Trends', fontsize=font_size1)
ax.set_xlabel("Time",fontsize=font_size2)
ax.set_ylabel("Precipitation [mm]",fontsize=font_size2)

legend1='GCM - Raw Data'
legend2='GCM - Mean Bias Corrected'
legend3='GCM - Quantile Mapping'
legend4='GCM - BCCAQv2'
legend5='Observations'
legend6='Trend - GCM Raw Data- y=2.177e-05x+ 1.458'
legend7='Trend - GCM Mean Bias Corrected- y=2.714e-06x + 2.542'
legend8='Trend - GCM Quantile Mapping- y=4.322e-06x + 2.495'
legend9='Trend - GCM BCCAQv2- y=5.056e-06x + 2.575'
legend10='Trend - Observations- y=2.210e-05x + 2.438'


legend_col3 = ['y=2.177*10^(-5)x + 14.558','y=0.00016x + 10.558','y=0.00014x + 10.690','y=0.00015x + 10.889','y=0.00014x + 10.690']


#Raw
# =============================================================================
# ax.plot(t, var1, '.', label=legend1, markersize=3, color='orchid', alpha= 1.0)
# =============================================================================
#Mean Bias Corrected
# =============================================================================
# ax.plot(t, var2, '.', label=legend2, markersize=3, color='palegreen', alpha= 1.0)
# =============================================================================
#Quantile Mapping
ax.plot(t, var3, '.', label=legend3, markersize=3, color='seagreen', alpha= 1.0)
# =============================================================================
# #BCCAQv2
# ax.plot(t, var4, '.', label=legend4, markersize=4, color='coral', alpha= 1.0)
# =============================================================================
#Observed
ax.plot(t, var5, '.', label=legend5, markersize=5, color='black', alpha= 1.0)

# plotting regression lines
# #Raw
# =============================================================================
# ax.plot(t, line1, '-', label=legend6,color='orchid',linewidth=3.5)     
# =============================================================================
# #Mean Bias Corrected
# ax.plot(t, line2, '-', label=legend7,color='palegreen',linewidth=3.5)        
# =============================================================================
# =============================================================================
#Quantile Mapping
ax.plot(t, line3, '-', label=legend8,color='seagreen',linewidth=3.5)
# =============================================================================
# #BCCAQv2
# ax.plot(t, line4, '-', label=legend9,color='coral',linewidth=3.5)        
# =============================================================================
# #Observed
ax.plot(t, line5, '--', label=legend10,color='black',linewidth=3.5)

        
plt.xticks(fontsize=font_size2)
plt.yticks(fontsize=font_size2)
lg=plt.legend(fontsize=14, bbox_to_anchor=(0.95,-0.1), ncol=2) #loc=2)
lg.draw_frame(False)
plt.tight_layout()
plt.savefig(output +'trend_1981_2010_pr_obs_qm2.png')
plt.plot()

print('It took', time.time()-start, 'seconds.')
