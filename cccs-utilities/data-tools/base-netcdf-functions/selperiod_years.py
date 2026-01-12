import time
import numpy as np
import pandas as pd
import xarray
import matplotlib.pyplot as plt


#####################################
def selperiod_years(file,first_year, last_year, show_newPer='YES', save_nerCDF='NO'):
    """ This function will open a netcDF file, select all time steps from the date corresponding to first_year to 
	the date corresponding to the last year and same the new file in netCDF
	file = put here the path and the name of the original netCDF file
	first_year = year from which the selection begins ; ex. '1982'
	last_year = last year in the selected period; ex. '2000'
	show_newPer= put 'YES' if you want to verify the years selected
	save_nerCDF= if you want to save the file put here the path and the name of the netCDF file to save; 
	if you don't want to save it, put 'NO' and use the file locally for other operations.
    """
    ds = xarray.open_dataset(file)
    new_data=ds.sel(time=slice(first_year,last_year))
    if show_newPer=='YES':
        print('There are ' + str(new_data.time.values.size) + ' time steps')
        print('The first time stemp is : ' + str(new_data.time.values[0]))
        print('The second time stemp is : ' + str(new_data.time.values[1]))
        print('The last time stemp is : ' + str(new_data.time.values[-1]))

    if save_nerCDF!='NO':
        new_data.to_netcdf(save_nerCDF)
    return new_data

