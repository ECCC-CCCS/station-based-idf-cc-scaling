import time
import pandas as pd
import xarray


def selPoint(file, var, latitude, longitude, save_nerCDF='NO',save_CSV='NO'):
    """ This function will open a netcDF file, select data for the grid point situated closest 
	to latitude and longitude indicated and save the new file in netCDF or CSV.
	The function supposes that the file has the spatial dimensions noted with lat and lon.
	file = put here the path and the name of the original netCDF file
	var = put here the name of the variable, ex. 'tas'
	latitude, longitude= put here the approximative coordinates of the point
	save_CSV= if you want to save the file put here the path and the name of the CSV file to save; 
	if you don't want to save it, put 'NO' and use the file locally for other operations
	save_nerCDF= if you want to save the file put here the path and the name of the netCDF file to save;  
	if you don't want to save it, put 'NO' and use the file locally for other operations.
    """
    ds = xarray.open_dataset(file)
    dataSel = ds[var].sel(lat=latitude, lon=longitude, method='nearest')
    t = pd.to_datetime(dataSel.time.values)
    timestring = pd.Series(t.strftime('%Y-%m-%d'))
    YYstring = pd.Series(t.strftime('%Y'))
    MMstring = pd.Series(t.strftime('%m'))
    DDstring = pd.Series(t.strftime('%d'))
    values=pd.Series(dataSel.values)
    table = pd.concat( [timestring, YYstring, MMstring, DDstring, values], axis=1)
    table.columns=['date', 'year', 'month', 'day', var]


    if save_CSV!='NO':
        table.to_csv(save_CSV, sep=',',index=False)

    if save_nerCDF!='NO':
        dataSel.to_netcdf(save_nerCDF)
    
    return table

