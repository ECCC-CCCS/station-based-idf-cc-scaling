import time
import numpy as np
import pandas as pd
import xarray
import matplotlib.pyplot as plt


#####################################
#def annual_mean_3D(file, show_newPer='YES', save_nerCDF='NO'):
""" This function will open an 3D netcDF file, compute the time mean for each year and save the new file in netCDF.
	The date indicated for each year is the first time step of the corresponding year.
	file = put here the path and the name of the original netCDF file
	show_newPer= put 'YES' if you want to verify the time dimension information
	save_nerCDF= if you want to save the file put here the path and the name of the netCDF file to save; 
	if you don't want to save it, put 'NO' and use the file locally for other operations.
"""


#we start a chronometer
start = time.time()
input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Precipitation/26/pr_rcp26_bcccsm11_monthlyMean.nc'
var='pr'
# Put in output the path and the name of the file you want to create
output='C:/Users/degroots/Temporary Files/Data/Outputs/main_function_outputs/test24.n
# I will use the following line if I want to save the new file as netCDF 
#annual_mean_3D(input, show_newPer='YES', save_nerCDF=output)




ds = xarray.open_dataset(input)  
new_data=ds.resample(time="AS").mean('time')
new_data.attrs['Description'] = ' annual mean values '
#if show_newPer=='YES':
print('There are ' + str(new_data.time.values.size) + ' time steps')
print('The first time stemp is : ' + str(new_data.time.values[0]))
print('The second time stemp is : ' + str(new_data.time.values[1]))
print('The last time stemp is : ' + str(new_data.time.values[-1]))

#if save_nerCDF!='NO':
new_data.to_netcdf()
#return new_data

################### EXAMPLE ##############
#we start a chronometer
start = time.time()



# we print the number of seconds it took to run the script
print('It took', time.time()-start, 'seconds.')
