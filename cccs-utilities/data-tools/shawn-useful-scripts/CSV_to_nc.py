import pandas as pd
import xarray as xr


kw = dict(sep=',',
          header=None, index_col=0, squeeze=True, engine='python')

input='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/05 - Personal/DeGroot/SPEI Project/data/Historic SPEI/'
fld='SPEI_12_mod.csv'

fileout='SPEI_12_gridded_test.nc'

df=pd.read_csv(input+fld, **kw)
df.name='SPEI'

# create xarray Dataset from Pandas DataFrame
xds = xr.Dataset.from_dataframe(df)

xds.data_vars{'SPEI': df[3:]}

# add variable attribute metadata
xds.attrs={'units':'standard deviations', 'long_name':'Standardized Precipitation Evapotranspiration Index'}
#xds['NAO'].attrs={'units':'1', 'long_name':'North Atlantic Oscillation'}

# add global attribute metadata
xds.attrs={'Conventions':'CF-1.0', 'title':'Historical 12 month Standardized Precipitation Evapotranspiration Index across Canada',
           'summary':"""This dataset provides 50 km gridded, 12-month Standardized Precipitation Evapotranspiration Index (SPEI) values across land regions of Canada. Over southern areas of the country (south of 60°N)																			
data are from 1900-2011 while in northern areas, the time period is shorter (approximately 1950-2011).The SPEI is a commonly used drought index, which evaluates the deviation of moisture deficit																			
calculated as the difference between precipitation and potential evapotranspiration, the latter determined by temperature. It can be calculated on a variety of temporal scales (e.g. 1,3,12 & 24 months).																			
The values are standardized with negative SPEI representing drier than normal conditions and positive values corresponding to wetter than normal conditions. The SPEI are calculated using precipitation																			
and temperature input from the Canadian gridded (CANGRD) dataset. For each grid point, the data consist of consecutive monthly values that represent the SPEI values for the previous 12 months.																			
"""}

# save to netCDF
xds.to_netcdf(input+fileout)



# =============================================================================
# Then running ncdump -h SPEI_12_gridded_test.nc produces:
# 
# netcdf SPEI_12_gridded_test {
# dimensions:
#         dates = 782 ;
# variables:
#         double dates(dates) ;
#                 dates:units = "days since 1950-01-06 00:00:00" ;
#                 dates:calendar = "proleptic_gregorian" ;
#         double NAO(dates) ;
#                 NAO:units = "1" ;
#                 NAO:long_name = "North Atlantic Oscillation" ;
#         double AO(dates) ;
#                 AO:units = "1" ;
#                 AO:long_name = "Arctic Oscillation" ;
# 
# // global attributes:
#                 :title = "AO and NAO" ;
#                 :summary = "Arctic and North Atlantic Oscillation Indices" ;
#                 :Conventions = "CF-1.0" ;
# 
# =============================================================================
