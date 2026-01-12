import xarray
import matplotlib.pyplot as plt
import time
import glob, os

def change_to_mm_per_day(file, var, save='NO', figure='YES'):
    """ This function transforms kg m-2 s-1 in mm/day for a netCDF file and save the new file as netCDF
	file = put here the path and the name of the netCDF file in kg m-2 s-1
	var = put here the name of the variable you want to change from kg m-2 s-1 to mm/day
	save = if you want to save the file put here the path and the name of the netCDF file in mm/day; if you don't want to save it, put 'NO' and use the file locally for other operations
	figure = put 'YES' if want to see a figure with the mean over the entire period.
    """
    ds = xarray.open_dataset(file)
    data_mmday= ds[var]*86400
    if save!='NO':
        ds[var]= data_mmday
        ds[var].attrs['Description'] = var+' expressed in mm/day'
        ds[var].attrs["units"] = "mm/day"
        ds.to_netcdf(save)
    if figure=='YES':
        fig1 = plt.figure()
        data_mmday.mean(dim='time').plot.contourf(x='lon', y='lat', cmap='BrBG_r', levels=22)
        plt.show()
    return data_mmday

