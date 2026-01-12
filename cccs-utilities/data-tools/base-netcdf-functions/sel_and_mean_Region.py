import time
import numpy as np
import pandas as pd
import xarray
import glob, os

def sel_and_mean_Region(file,var,lat_bottom, lat_top, lon_left, lon_right, show_regInfo='YES', save_CSV='NO'):
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
    ds = xarray.open_dataset(file)
    latB = ds.lat.sel(lat=lat_bottom, method='nearest', tolerance=5)
    latT = ds.lat.sel(lat=lat_top, method='nearest', tolerance=5)
    lonL = ds.lon.sel(lon=lon_left, method='nearest', tolerance=5)
    lonR = ds.lon.sel(lon=lon_right, method='nearest', tolerance=5)
    dataSel = ds.sel(lat=slice(latB.values, latT.values), lon=slice(lonL.values, lonR.values))
    lonsM, latsM = np.meshgrid(dataSel.lon.values, dataSel.lat.values)
    wgtmat = np.cos(np.deg2rad(latsM))
    mean_Var = np.zeros(dataSel.time.size)  # Preallocation
    for i in range(dataSel.time.size):
        mean_Var[i] = np.nansum(dataSel[var].values[i] * wgtmat) / (wgtmat).sum()

    if show_regInfo=='YES':
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
    t = pd.to_datetime(dataSel.time.values)
    timestring = pd.Series(t.strftime('%Y-%m-%d'))
    YYstring = pd.Series(t.strftime('%Y'))
    MMstring = pd.Series(t.strftime('%m'))
    DDstring = pd.Series(t.strftime('%d'))
    values=pd.Series(mean_Var)
    table = pd.concat( [timestring, YYstring, MMstring, DDstring, values], axis=1)
    table.columns=['date', 'year', 'month', 'day', 'Spatial mean']

    if save_CSV!='NO':
        table.to_csv(save_CSV, sep=',',index=False)
    return table

