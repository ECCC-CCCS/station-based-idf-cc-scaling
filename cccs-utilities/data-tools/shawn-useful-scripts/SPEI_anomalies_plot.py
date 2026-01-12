import xarray as xr
import pandas as pd
import numpy as np
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
np.set_printoptions(threshold=sys.maxsize)

start= time.time()

input= 'C:/Users/degroots/Temporary Files/Data/SPEI Drought/SPEI_50percentile_ensemble_rcp26_MON_1900_2100.nc'
output= 'C:/Users/degroots/Temporary Files/Data/SPEI Drought/outputs/'
fld='testing.nc'
latitude=50.0405
longitude=-110.6764


first_date= '2070'
last_date= '2100'

ds= xr.open_dataset(input)
#dataSel= ds['spei']

values= ds['spei'].values
#values.to_netcdf(output+fld)
#np.savetxt('test.csv', values)
dataSel= ds['spei'].sel(latitude=latitude, longitude=longitude, method='nearest')


new_data=dataSel.sel(time=slice(first_date,last_date))

# have selected period, region, and resampled to annual FREQ
new_data2=new_data.resample(time="AS").mean('time')
new_data3= new_data2[:, 0]
#.values
#new_data3=new_data2.flatten()


t= pd.date_range('2070','2100', freq='AS')

timestring = pd.Series(t.strftime('%Y-%m-%d'))
YYstring = pd.Series(t.strftime('%Y'))
MMstring = pd.Series(t.strftime('%m'))
DDstring = pd.Series(t.strftime('%d'))
values=pd.Series(new_data3)    
table = pd.concat([timestring, YYstring, MMstring, DDstring, values], axis=1)
table.columns=['date', 'year', 'month', 'day', 'SPEI']
table = table.melt(id_vars = ['date','day','month','year'])


# matplotlib time series
fig= plt.figure()
x= table['year']
y= table['value']


tick_spacing = 10

fig, ax = plt.subplots(1,1)

ax.axhline(c= 'k')
#ax.xlabel('Years')
#ax.ylabel('SPEI')
plt.title("""SPEI Values Anomaly- Medicine Hat, AB- 2070-2100
     RCP 2.6, Model Ensemble- 1950-2005 Reference Period""")
ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax.plot(x,y)
plt.xlabel('Years')
plt.ylabel('SPEI')
#plt.show()
plt.savefig(output+'mc_test_29.png', dpi= 400)

#plt.plot(x,y)

#plt.xticks(np.arange(2070,2100,10))

#plt.show()



print('It took', time.time()-start, 'seconds.')