import xarray

input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Temperature/26/tmean_rcp26_bnuesm_monthlyMean.nc'
output='C:/Users/degroots/Temporary Files/Data/Outputs/main_function_outputs/'
threshold=15.0
varName='tas'


fileout = fld[:-6] + '_annual_number_greater.nc'


ds = xarray.open_dataset(input+fld)
ds2 = ds[varName]
ds3 = ds2.where(ds2 > threshold)
ds4=ds3 * 0.0 + 1.0
ds4=ds4.to_datetimeindex()
new_data=ds4.resample(time="AS").sum('time')
new_data.attrs['Description'] = ' annual number of values greater than '+ str(threshold)

print('There are ' + str(new_data.time.values.size) + ' time steps')
print('The first time stemp is : ' + str(new_data.time.values[0]))
print('The second time stemp is : ' + str(new_data.time.values[1]))
print('The last time stemp is : ' + str(new_data.time.values[-1]))

new_data.to_netcdf(output+fileout)

