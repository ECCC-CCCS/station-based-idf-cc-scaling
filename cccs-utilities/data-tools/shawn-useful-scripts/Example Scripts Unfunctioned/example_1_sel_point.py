import pandas as pd
import xarray

latitude=58
longitude=102.5


input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Precipitation/26/'
fld='pr_rcp26_bcccsm11_monthlyMean.nc'
var='pr'
output='C:/Users/degroots/Temporary Files/Python/netCDF files/Training Outputs/other/'
new_netCDF=fld[:-3] + 'degroot.nc'


ds = xarray.open_dataset(input+fld)
dataSel = ds[var].sel(lat=latitude, lon=longitude, method='nearest')
t= pd.date_range('1900-01-16 12:00:00',' 2101-1-16 12:00:00', freq='M' )
timestring = pd.Series(t.strftime('%Y-%m-%d'))
YYstring = pd.Series(t.strftime('%Y'))
MMstring = pd.Series(t.strftime('%m'))
DDstring = pd.Series(t.strftime('%d'))
values=pd.Series(dataSel.values)
table = pd.concat( [timestring, YYstring, MMstring, DDstring, values], axis=1)
table.columns=['date', 'year', 'month', 'day', var]

table.to_csv(output+ 'degroot.csv', sep=',',index=False)



