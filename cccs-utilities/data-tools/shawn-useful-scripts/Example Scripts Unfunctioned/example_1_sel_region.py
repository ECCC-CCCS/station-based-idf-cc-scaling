import xarray

input= 'C:/Users/degroots/Temporary Files/Python/netCDF files/Training/CMIP 5/New_Precipitation/26/'
fld='pr_rcp26_bcccsm11_monthlyMean.nc'
var='pr'
output='C:/Users/degroots/Temporary Files/Python/netCDF files/Training Outputs/other/'
new_file=fld[:-3]+'_new3.nc'


lat_bottom=50
lat_top=55
lon_left=360-80
lon_right=360-75


ds = xarray.open_dataset(input + fld, decode_times=False)
latB = ds.lat.sel(lat=lat_bottom, method='nearest', tolerance=5)
latT = ds.lat.sel(lat=lat_top, method='nearest', tolerance=5)   
lonL = ds.lon.sel(lon=lon_left, method='nearest', tolerance=5)
lonR = ds.lon.sel(lon=lon_right, method='nearest', tolerance=5)
dataSel = ds.sel(lat=slice(latB.values, latT.values), lon=slice(lonL.values, lonR.values))
dataSel.to_netcdf(output + new_file)

