import time
import xarray
import glob, os
import pandas as pd

#####################################
def seasonal_mean_1D_sepM_list(input, list, varName, save_csv='NO'):
    """ This function will open a list with 1D netcDF files, compute the time mean for each season and save 
	the new files in 4 cvs files, one for each season; Each netcdf file will be saved on a different column in the csv file.
	The date indicated for each year is the last time step of the corresponding season in the year.
	input = put here the path to the 1D netCDF files
	list = put here the list with the names of all 1D netCDF files you want
	varName = put here the name of the variable, ex. 'tas'
	save_csv= if you want to save the file put here the path and the name of the csv file to save without .csv
	(the program will add the seasons at the end of the name and the .csv)
	if you don't want to save it, put 'NO' and use the file locally for other operations.
    """
    def is_winter(month):
        return (month >= 1) & (month <= 2)
    def is_spring(month):
        return (month >= 3) & (month <= 5)
    def is_summer(month):
        return (month >= 6) & (month <= 8)
    def is_autumn(month):
        return (month >= 9) & (month <= 11)

    fld = list[:1][0]
    ds = xarray.open_dataset(input+fld)
    new_data=ds.resample(time='Q-NOV').mean('time') 
    new_data.attrs['Description'] = ' seasonal mean values '

    winter_data = new_data.sel(time=is_winter(new_data['time.month']))
    spring_data = new_data.sel(time=is_spring(new_data['time.month']))
    summer_data = new_data.sel(time=is_summer(new_data['time.month']))
    autumn_data = new_data.sel(time=is_autumn(new_data['time.month']))

    winter_table = pd.DataFrame(winter_data[varName].values, columns=['m1'], index=winter_data['time.year'])
    spring_table = pd.DataFrame(spring_data[varName].values, columns=['m1'], index=spring_data['time.year'])
    summer_table = pd.DataFrame(summer_data[varName].values, columns=['m1'], index=summer_data['time.year'])
    autumn_table = pd.DataFrame(autumn_data[varName].values, columns=['m1'], index=autumn_data['time.year'])
    print(fld, 'm1')
    for fld, nr in zip(list[1:], range(2, len(list) + 2)):
        print(fld, 'm' + str(nr))
        nameModel = 'm' + str(nr)
        ds = xarray.open_dataset(input+fld)
        new_data=ds.resample(time='Q-NOV').mean('time')
        new_data.attrs['Description'] = ' seasonal mean values '

        winter_data = new_data.sel(time=is_winter(new_data['time.month']))
        spring_data = new_data.sel(time=is_spring(new_data['time.month']))
        summer_data = new_data.sel(time=is_summer(new_data['time.month']))
        autumn_data = new_data.sel(time=is_autumn(new_data['time.month']))

        winter_table[nameModel] = pd.DataFrame(winter_data[varName].values, columns=[nameModel], index=winter_data['time.year'])
        spring_table[nameModel] = pd.DataFrame(spring_data[varName].values, columns=[nameModel], index=spring_data['time.year'])
        summer_table[nameModel] = pd.DataFrame(summer_data[varName].values, columns=[nameModel], index=summer_data['time.year'])
        autumn_table[nameModel] = pd.DataFrame(autumn_data[varName].values, columns=[nameModel], index=autumn_data['time.year'])

    if save_csv!='NO':
        winter_table.to_csv(save_csv+'_winter.csv', sep=',')
        spring_table.to_csv(save_csv+'_spring.csv', sep=',')
        summer_table.to_csv(save_csv+'_summer.csv', sep=',')
        autumn_table.to_csv(save_csv+'_autumn.csv', sep=',')
    return winter_table, spring_table, summer_table, autumn_table

