import time
import numpy as np
import pandas as pd
import xarray
import matplotlib.pyplot as plt


#####################################
#def selperiod_date(file,first_date, last_date, show_newPer='YES', save_nerCDF='NO'):
""" This function will open an netcDF file, select all time steps from the date corresponding to 
	first_date to the date corresponding to the last_date and save the new file in netCDF
	file = put here the path and the name of the original netCDF file
	first_date = date from which the selection begins ; ex. '2000-02-15'
	last_date = last date in the selected period; ex. '2002-10-10'
	show_newPer= put 'YES' if you want to verify the years selected
	save_nerCDF= if you want to save the file put here the path and the name of the netCDF file to save; 
	if you don't want to save it, put 'NO' and use the file locally for other operations.
"""


start = time.time()

###########################################

input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Precipitation/26/pr_rcp26_bcccsm11_monthlyMean.nc'
var='pr'

# Put in output the path and the name of the file you want to create
output='C:/Users/degroots/Temporary Files/Data/Outputs/main_function_outputs/test22.nc'

# put here the first and the last date
first_date='2000-02-14'
last_date='2002-10-10'

#dataT=selperiod_date(input, first_date,last_date, show_newPer='YES', save_nerCDF='NO')

#selperiod_date(input, first_date,last_date, show_newPer='YES', save_nerCDF=output)



ds = xarray.open_dataset(input)
new_data=ds.sel(time=slice(first_date,last_date))
#if show_newPer=='YES':
print('There are ' + str(new_data.time.values.size) + ' time steps')
print('The first time stemp is : ' + str(new_data.time.values[0]))
print('The second time stemp is : ' + str(new_data.time.values[1]))
print('The last time stemp is : ' + str(new_data.time.values[-1]))

#if save_nerCDF!='NO':
new_data.to_netcdf(output)
#return new_data

################### EXAMPLE ##############


print ('It took', time.time()-start, 'seconds.')
