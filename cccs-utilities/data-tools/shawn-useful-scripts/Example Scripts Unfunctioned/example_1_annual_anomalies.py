import xarray

input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Temperature/26/'
output='C:/Users/degroots/Temporary Files/Data/Outputs/main_function_outputs/'

fld='tmean_rcp26_bcccsm11m_monthlyMean.nc'

first_year= '1980'
last_year= '2005'

fileout=fld[:-3]+'_anomalies2.nc'

ds=xarray.open_dataset(input+fld)

new_data=ds.resample(time='AS').mean('time')

ref_data=ds.sel(time=slice(first_year, last_year))
ref_mean=ref_data.mean('time')

annual_anomalies=new_data-ref_mean
annual_anomalies.attrs['Description']='annual anomalies'
annual_anomalies.attrs['CDI']=ds.attrs['CDI']
annual_anomalies.attrs['Conventions']=ds.attrs['Conventions']


annual_anomalies.attrs['GCM institute']=ds.attrs['institute_id']
annual_anomalies.attrs['GCM']=ds.attrs['model_id']


print('There are ' + str(new_data.time.values.size) + ' time steps')
print('The first time stemp is : ' + str(new_data.time.values[0]))
print('The second time stemp is : ' + str(new_data.time.values[1]))
print('The last time stemp is : ' + str(new_data.time.values[-1]))

annual_anomalies.to_netcdf(output+fileout)

    