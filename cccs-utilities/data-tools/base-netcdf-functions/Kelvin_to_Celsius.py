import time
import xarray
import matplotlib.pyplot as plt
import glob, os

def Kelvin_to_Celsius(file, var, save='NO', figure='YES'):
    """ This function transforms Kelvin in Celsius for a netCDF file and save the new file as netCDF
	file = put here the path and the name of the netCDF file in Kelvin
	var = put here the name of the variable you want to change from Kelvin to Celsius
	save = if you want to save the file put here the path and the name of the netCDF file in Celsius; 
	if you don't want to save it, put 'NO' and use the file locally for other operations
	figure = put 'YES' if want to see a figure with the mean over the entire period.
    """
    ds = xarray.open_dataset(file)
    data_Celsius= ds[var]- 273.16
    if save!='NO':
        ds[var]= data_Celsius
        ds[var].attrs['Description'] = var+' expressed in Celsius'
        ds[var].attrs["units"] = "degrees_Celsius"
        ds.to_netcdf(save)
    if figure=='YES':
        fig1 = plt.figure()
        data_Celsius.mean(dim='time').plot.contourf(x='lon', y='lat', cmap='BrBG_r', levels=22)
        plt.show()
    return data_Celsius

