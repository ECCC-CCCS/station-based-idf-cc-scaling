import time
import numpy as np
import pandas as pd
import xarray
import matplotlib.pyplot as plt

def spatial_mean(file,var, save_CSV='NO'):
    """ This function will open a netcDF file, make a area-weighted averages of gridded spatial data and save the new file. 
	The function supposes that the file has the spatial dimensions noted with lat and lon.
	file = put here the path and the name of the original netCDF file
	var = put here the name of the variable, ex. 'tas'
	save_CSV= if you want to save the file put here the path and the name of the CSV file to save; 
	if you don't want to save it, put 'NO' and use the file locally for other operations.
    """
    ds = xarray.open_dataset(file)
    dataSel = ds[var]
    lonsM, latsM = np.meshgrid(dataSel.lon.values, dataSel.lat.values)
    wgtmat = np.cos(np.deg2rad(latsM))
    mean_Var = np.zeros(dataSel.time.size)  # Preallocation
    for i in range(dataSel.time.size):
        mean_Var[i] = (dataSel.values[i] * wgtmat).sum() / (wgtmat).sum()

    t = pd.to_datetime(dataSel.time.values)
    timestring = t.strftime('%Y-%m-%d')
    table = pd.DataFrame(mean_Var, index=timestring, columns=['Mean'])

    if save_CSV!='NO':
        table.to_csv(save_CSV, sep=',')
    return table

