import xarray

input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Precipitation/26/pr_rcp26_bcccsm11_monthlyMean.nc'
var='pr'

output='C:/Users/degroots/Temporary Files/Data/Outputs/main_function_outputs/test23.nc'

first_yy='2000'
last_yy='2002'

ds = xarray.open_dataset(input)
new_data=ds.sel(time=slice(first_yy,last_yy))

new_data.to_netcdf(output)
