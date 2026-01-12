import time
import numpy as np
import pandas as pd
import xarray
import glob, os

#def sel_and_mean_Region(file,var,lat_bottom, lat_top, lon_left, lon_right, show_regInfo='YES', save_CSV='NO'):
""" This function will open an netcDF file, select data situated into a rectangle defined by the closest points to lat_bottom, 
lat_top, lon_left, lon_right, make an area-weighted average of gridded spatial data and save the new file. 
The function supposes that the file has the spatial dimensions noted with lat and lon.
file = put here the path and the name of the original netCDF file
var = put here the name of the variable, ex. 'tas'
lat_bottom, lat_top, lon_left, lon_right= put here the approximative coordinates of the region
show_newPer= put 'YES' if you want to verify the lat and lon selected
save_CSV= if you want to save the file put here the path and the name of the CSV file to save; 
if you don't want to save it, put 'NO' and use the file locally for other operations.
"""
    
    

#we start a chronometer
start = time.time()

# Put in input the path to the netCDF file you want
input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Precipitation/26/'
# Put here the name of the netCDF file
fld='pr_rcp26_bcccsm11_monthlyMean.nc'
# Put in output the path to the folder were you want to save the new csv file
output='C:/Users/degroots/Temporary Files/Data/Outputs/main_function_outputs/test_new_shawn.csv'
# Put here the name of the new csv file
new_fld='test_new_shawn_SM.csv'

# Put here the name of the netCDF variable
var='pr'


# Put here the corners of the region you want
# Attention aux longitude if expressed in values from -180 to 180 or from 0 to 360; use the format of your data
lat_bottom=42.2
lat_top=65.3
lon_left=200.1
lon_right=255.4

    
ds = xarray.open_dataset(input+fld)
latB = ds.lat.sel(lat=lat_bottom, method='nearest', tolerance=5)
latT = ds.lat.sel(lat=lat_top, method='nearest', tolerance=5)
lonL = ds.lon.sel(lon=lon_left, method='nearest', tolerance=5)
lonR = ds.lon.sel(lon=lon_right, method='nearest', tolerance=5)
# getting the slice for region
dataSel = ds.sel(lat=slice(latB.values, latT.values), lon=slice(lonL.values, lonR.values))
# pulling lat and lon values from DS
lonsM, latsM = np.meshgrid(dataSel.lon.values, dataSel.lat.values)
#taking cosine of latitude values in radians
wgtmat = np.cos(np.deg2rad(latsM))

# start with fresh array, length of time stamps
mean_Var = np.zeros(dataSel.time.size)  # Preallocation

# iterate through range, multliply each pr by cosine lat values, append to new variable
for i in range(dataSel.time.size):
    mean_Var[i] = np.nansum(dataSel[var].values[i] * wgtmat) / (wgtmat).sum()

    #if show_regInfo=='YES':
print('There are ' + str(dataSel.lat.values.size) + ' grid points for latitudes')
print('The first latitude is : ' + str(dataSel.lat.values[0]))
print('The second latitude is : ' + str(dataSel.lat.values[1]))
print('The last latitude is : ' + str(dataSel.lat.values[-1]))
print('  ')
print('There are ' + str(dataSel.lon.values.size) + ' grid points for longitude')
print('The first longitude is : ' + str(dataSel.lon.values[0]))
print('The second longitude is : ' + str(dataSel.lon.values[1]))
print('The last longitude is : ' + str(dataSel.lon.values[-1]))
print('  ')
t= pd.date_range('1900-01-16 12:00:00',' 2101-1-16 12:00:00', freq='M' )
#t = pd.to_datetime(dataSel.time.values)
timestring = pd.Series(t.strftime('%Y-%m-%d'))
YYstring = pd.Series(t.strftime('%Y'))
MMstring = pd.Series(t.strftime('%m'))
DDstring = pd.Series(t.strftime('%d'))
values=pd.Series(mean_Var)
table = pd.concat( [timestring, YYstring, MMstring, DDstring, values], axis=1)
table.columns=['date', 'year', 'month', 'day', 'Spatial mean']

table.to_csv(output+new_fld, sep=',',index=False)
   

################ EXAMPLE 1 #######################




# we apply the function and we name also the new csv data to dataS to use it further in python
#dataS= sel_and_mean_Region(input+fld,varName,lat_bottom, lat_top, lon_left, lon_right, show_regInfo='YES', save_CSV=output+new_fld)

# if we want to have a quick view of the new data:
#dataS

# if we want a quick plot of the data
#dataS.index=dataS['date']
#dataS['Spatial mean'].plot()

# we print the number of seconds it took to run the script
print('It took', time.time()-start, 'seconds.')

