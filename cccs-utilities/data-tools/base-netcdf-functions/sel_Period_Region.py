import time
import xarray
import glob, os


def sel_Period_Region(file,first_date, last_date, lat_bottom, lat_top, lon_left, lon_right, show_regInfo='YES', save_nerCDF='NO'):
    """ This function will open a netcDF file, select data situated into a rectangle defined by the closest points to lat_bottom, 
	lat_top, lon_left, lon_right, and the time period and save the new file in netCDF. 
	The function supposes that the file has the spatial dimensions noted with lat and lon.
	file = put here the path and the name of the original netCDF file
	lat_bottom, lat_top, lon_left, lon_right= put here the approximative coordinates of the region
	show_newPer= put 'YES' if you want to verify the lat and long selected
	first_date = date from which the selection begins ; ex. '2000-02-15'
	last_date = last date in the selected period; ex. '2002-10-10'
	save_nerCDF= if you want to save the file put here the path and the name of the netCDF file to save; 
	if you don't want to save it, put 'NO' and use the file locally for other operations.
    """
    ds = xarray.open_dataset(file)
    latB = ds.lat.sel(lat=lat_bottom, method='nearest', tolerance=5)
    latT = ds.lat.sel(lat=lat_top, method='nearest', tolerance=5)
    lonL = ds.lon.sel(lon=lon_left, method='nearest', tolerance=5)
    lonR = ds.lon.sel(lon=lon_right, method='nearest', tolerance=5)
    dataSel = ds.sel(lat=slice(latB.values, latT.values), lon=slice(lonL.values, lonR.values),time=slice(first_date,last_date))
    if show_regInfo=='YES':
        print('There are ' + str(dataSel.time.values.size) + ' time steps')
        print('The first time step is : ' + str(dataSel.time.values[0]))
        print('The second time step is : ' + str(dataSel.time.values[1]))
        print('The last time step is : ' + str(dataSel.time.values[-1]))
        print('  ')
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

    if save_nerCDF!='NO':
        dataSel.to_netcdf(save_nerCDF)
    return dataSel

