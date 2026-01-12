import pandas as pd
import xarray as xr
import numpy as np

input='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/05 - Personal/DeGroot/Support Desk Cases/other/'
fld='boxav.nc'

output='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/05 - Personal/DeGroot/Support Desk Cases/other/'

ds=xr.open_dataset(input+fld)

# put here the first and the last date
first_yy='2019-01-01'
last_yy='2019-01-01'

#ds['time'] = xr.decode_cf(ds).time
ds = xr.open_dataset(input+fld)#, decode_times=False)
new_data=ds.sel(time=slice(first_yy,last_yy))


lon_new=[5.5,6,6.5,7]
lat_new=[45,45.5,46,46.5]

values_new=new_data.tasmax.values
values_new2=values_new.flatten()
values_new3=float(values_new2)

#values_new4=np.arange(values_new3,values_new3,4)

values_new4=np.repeat(values_new3,4)

values_new6=np.full((4, 4), values_new3)

time=new_data.time
#values_new4=values_new4.tolist()


#putting back in:
# =============================================================================
# 
# new_data.lon=lon_new
# new_data.lat=lat_new
# new_data.tasmax.values=values_new4
# =============================================================================
# =============================================================================
# 
# new_data.assign(tasmax.values=values_new4)
# 
# new_data.assign_coords(lon=lon_new)
# new_data.assign_coords(lat=lat_new)
# 
# =============================================================================

             
           
# Create some dimensions
x = lon_new
y = lat_new
(yy, xx) = np.meshgrid(y,x)

# Make two different DataArrays with equal dimensions
var1 = xr.DataArray(np.random.randn(len(x),len(y)),coords=[x, y],dims=['x','y'])


#var2=var1.assign(Tasmax= values_new3)

var1.values=values_new6

var2=var1.to_dataset(name='tasmax')

#var1=var1.rename({x:'lon'})


print(var1)

#var1.to_netcdf(output+'testing.nc')


# =============================================================================
# 
# # Save one DataArray as dataset
# ds_test = var1.to_dataset(name = 'var1')
# ds_test.assign(tasmax.values=values_new4)
# =============================================================================
