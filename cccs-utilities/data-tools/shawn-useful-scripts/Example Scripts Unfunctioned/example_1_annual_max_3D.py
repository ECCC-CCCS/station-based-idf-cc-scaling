import xarray

input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Precipitation/26/pr_rcp26_bcccsm11_monthlyMean.nc'
var='pr'

output='C:/Users/degroots/Temporary Files/Data/Outputs/main_function_outputs/test23.nc'

ds = xarray.open_dataset(input)
new_data=ds.resample(time="AS").max('time')
new_data.attrs['Description'] = ' annual maximum values '

new_data.to_netcdf(output)
