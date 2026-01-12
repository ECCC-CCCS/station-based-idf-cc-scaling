import time
import numpy as np
import pandas as pd
import xarray
import matplotlib.pyplot as plt


#####################################
def annual_anomalies_3D(file, first_year, last_year, show_newPer='YES', save_nerCDF='NO'):
    """ This function will open an 3D netcDF file, compute the anomalies for each year based on the selected reference 
    period and save the new file in netCDF. The date indicated for each year is the first time step of the corresponding year.
	file = put here the path and the name of the original netCDF file
	show_newPer= put 'YES' if you want to verify the time dimension information
	save_nerCDF= if you want to save the file put here the path and the name of the netCDF file to save; 
	if you don't want to save it, put 'NO' and use the file locally for other operations.
    """
    ds=xarray.open_dataset(file)
    new_data=ds.resample(time='AS').mean('time')
    ref_data=ds.sel(time=slice(first_year, last_year))
    ref_mean=ref_data.mean('time')
    annual_anomalies=new_data-ref_mean
    annual_anomalies.attrs['Description']='annual anomalies'
    annual_anomalies.attrs['CDI']=ds.attrs['CDI']
    annual_anomalies.attrs['Conventions']=ds.attrs['Conventions']
    annual_anomalies.attrs['project']='CMIP5'
    annual_anomalies.attrs['experiment']=ds.attrs['experiment_id']
    annual_anomalies.attrs['institute']=ds.attrs['institution']
    annual_anomalies.attrs['model']=ds.attrs['model_id']
    annual_anomalies['tas'].attrs['standard_name']= ds['tas'].attrs['standard_name']
    annual_anomalies['tas'].attrs['long_name']= ds['tas'].attrs['long_name']
    annual_anomalies['tas'].attrs['units']= 'Celsius'
    annual_anomalies['tas'].attrs['frequency']= 'annual'
    if show_newPer=='YES':
        print('There are ' + str(new_data.time.values.size) + ' time steps')
        print('The first time stemp is : ' + str(new_data.time.values[0]))
        print('The second time stemp is : ' + str(new_data.time.values[1]))
        print('The last time stemp is : ' + str(new_data.time.values[-1]))
    if save_nerCDF!='NO':
        annual_anomalies.to_netcdf(save_nerCDF)
    return annual_anomalies

