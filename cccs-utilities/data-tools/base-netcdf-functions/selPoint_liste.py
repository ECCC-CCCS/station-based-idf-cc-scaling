import time
import pandas as pd
import xarray
import glob, os

def selPoint_liste(input, liste, var, latitude, longitude, save_CSV='NO'):
    """ This function will open several netcDF files, for each of them will select data for
    the grid point situated closest to latitude and longitude indicated and save the information from all models in one csv
	input = put here the path to the netCDF files
	liste = put here the list with the names of all netCDF files you want
	var = put here the name of the variable, ex. 'tas'
	latitude, longitude= put here the approximative coordinates of the point
	save_CSV= if you want to save the file put here the path and the name of the CSV file to save; 
	if you don't want to save it, put 'NO' and use the file locally for other operations
    """
    fld = liste[:1][0]
    ds = xarray.open_dataset(input+fld)
    dataSel = ds[var].sel(lat=latitude, lon=longitude, method='nearest')
    t = pd.to_datetime(dataSel.time.values)
    timestring = pd.Series(t.strftime('%Y-%m-%d'))
    YYstring = pd.Series(t.strftime('%Y'))
    MMstring = pd.Series(t.strftime('%m'))
    DDstring = pd.Series(t.strftime('%d'))
    values=pd.Series(dataSel.values)
    table = pd.concat( [YYstring, MMstring, DDstring, values], axis=1)
    table.columns=['year', 'month', 'day', 'm1']
    table.index = timestring
    print fld, 'm1'
    for fld, nr in zip(liste[1:], range(2, len(liste) + 2)):
        print fld, 'm' + str(nr)
        nameModel = 'm' + str(nr)
        ds = xarray.open_dataset(input+fld)
        dataSel = ds[var].sel(lat=latitude, lon=longitude, method='nearest')
        t = pd.to_datetime(dataSel.time.values)
        timestring = pd.Series(t.strftime('%Y-%m-%d'))
        table[nameModel] = pd.DataFrame(dataSel.values, index=timestring, columns=[nameModel])

    if save_CSV!='NO':
        table.to_csv(save_CSV, sep=',',index=False)

    return table

