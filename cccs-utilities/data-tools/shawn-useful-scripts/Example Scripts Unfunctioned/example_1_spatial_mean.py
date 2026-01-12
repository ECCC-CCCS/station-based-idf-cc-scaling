import numpy as np
import xarray
import pandas as pd

input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Precipitation/26/'
fld= 'pr_rcp26_bcccsm11_monthlyMean.nc'

output='C:/Users/degroots/Temporary Files/Data/Outputs/main_function_outputs/'
fileout='test_spatial_mean.nc'

varName='pr'

ds = xarray.open_dataset(input+ fld)
dataSel = ds['pr']
lonsM, latsM = np.meshgrid(dataSel.lon.values, dataSel.lat.values)

wgtmat = np.cos(np.deg2rad(latsM))

mean_Var = np.zeros(dataSel.time.size)  

for i in range(dataSel.time.size):
        mean_Var[i] = (dataSel.values[i] * (wgtmat).sum() / (wgtmat).sum())

t = pd.to_datetime(dataSel.time.values)
timestring = pd.Series(t.strftime('%Y-%m-%d'))
YYstring = pd.Series(t.strftime('%Y'))
MMstring = pd.Series(t.strftime('%m'))
DDstring = pd.Series(t.strftime('%d'))
values=pd.Series(mean_Var)
table = pd.concat( [YYstring, MMstring, DDstring, values], axis=1)
table.columns=['year', 'month', 'day', 'm1']
table.index = timestring

table.to_csv(output+fileout, sep=',')

