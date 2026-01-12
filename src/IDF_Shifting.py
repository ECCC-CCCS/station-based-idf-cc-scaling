# Contains the functions in which all code currently exists

from glob import glob
import xarray as xr
import numpy as np
import xclim.indices as xci
from xclim.ensembles import create_ensemble
from tqdm import tqdm
from clisops.core import subset


# Tools developed for code
from src.Tools import reformat_historical_IDF
from src.IDF_Confidence_Intervals import calculate_percentiles, percent95_IDFs


# Get Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

# Must have the cccs-utilities downloaded into the directory
sys.path.append('cccs-utilities/data-tools')
sys.path.append('../custom_extractions')
import Thredds_extraction_functions
from ECCC_IDF_reader import read_ECCC_IDF
#%%
# Function that reads in temperature data from Thredds database and creates an ensemble of the models
def temperatureData_Download(em_scenarios: list[str]) -> xr.Dataset:
    '''Retreive temperature SSP temperature data from Thredds server
    Parameters:
    -----------
    em_scenarios : List[string]
        List of strings outlining the emission scenarios you wish to download
        
    Returns:
    --------
    temperature_data : xarray.Dataset
        Dataset containing the retrieved temperature information
    '''
    
    # NOTE: The ssp370 scenario contains two less models, in the final output the tg_mean variable at models 24 & 25
    #       are filled with NaN values
    ds = []
    print("Retrieving Temperature Data for SSPs through Thredds Server")
    # Cycle through each of the ssps and find the corresponding datasets
    for em in tqdm(em_scenarios):
        # Find the files in the CMIP6 database for selected SSP
        file_list = Thredds_extraction_functions.threddscall(
            em_scenarios=em,
            indices='tg_mean',
            frequency='YS',
            average=True
            )
        
        # Combine the datasets for the current SSP into one xarray dataset
        # NOTE: The OpenDAP Url had to be accessed using xarray backend, introduces a warning just ignore
        # Using the backends functionality from xarray is faster than the open_dataset method
        with warnings.catch_warnings():
            # I have tried and explicitly state which OpenDAP protocol to use but it runs slower... for some reason
            # As such directly ignore the UserWarning that appears
            warnings.simplefilter('ignore', UserWarning)
            ds.append(create_ensemble([f.opendap_url() for f in file_list]))
       

    
    # Combine each of the temperature xarrays into one large dataset on the SSP dimension and rename the variables
    temperature_data = xr.concat(ds, dim='ssp')
    temperature_data = temperature_data.rename_dims({'realization': 'model'})
    temperature_data = temperature_data.rename_vars({'realization': 'model'})
    temperature_data = temperature_data.assign_coords(ssp=em_scenarios)
   
    return temperature_data
    
#%%
# Function that reads in temperature data for the reference period from Thredds database and creates an ensemble of the models
def reftemperatureData_Download(em_scenarios: list[str]) -> xr.Dataset:
    '''Retreive temperature SSP temperature data from Thredds server
    Parameters:
    -----------
    em_scenarios : List[string]
        List of strings outlining the emission scenarios you wish to download
        
    Returns:
    --------
    temperature_data : xarray.Dataset
        Dataset containing the retrieved temperature information
    '''
    
    # NOTE: The ssp370 scenario contains two less models, in the final output the tg_mean variable at models 24 & 25
    #       are filled with NaN values
    ds_ref = []
    print("Retrieving Temperature Data for SSPs through Thredds Server")
    # Cycle through each of the ssps and find the corresponding datasets
    for em in tqdm(em_scenarios):
        # Find the files in the CMIP6 database for selected SSP
        ref_file_list=Thredds_extraction_functions.threddscall(em_scenarios=em,
                                                       indices='tg_mean',
                                                       frequency='YS',
                                                       average=False)
        
        # Combine the datasets for the current SSP into one xarray dataset
        # NOTE: The OpenDAP Url had to be accessed using xarray backend, introduces a warning just ignore
        # Using the backends functionality from xarray is faster than the open_dataset method
        with warnings.catch_warnings():
            # I have tried and explicitly state which OpenDAP protocol to use but it runs slower... for some reason
            # As such directly ignore the UserWarning that appears
            warnings.simplefilter('ignore', UserWarning)
            ds_ref.append(create_ensemble([f.opendap_url() for f in ref_file_list]))
        

    ds_ref_c=xr.concat(ds_ref,dim='ssp')
    ref_temp_data = subset.subset_time(ds_ref_c, start_date="1974-01-01", end_date="2005-01-01").mean(dim='time').load()
    ref_temp_data=ref_temp_data.rename_dims({'realization':'model'})
    ref_temp_data=ref_temp_data.rename_vars({'realization':'model'})
    ref_temp_data=ref_temp_data.assign_coords(ssp=em_scenarios)

    return ref_temp_data

#%%
def IDF_Builder(tempData: xr.Dataset,
                ref_temp_data: xr.Dataset,
                IDF_files: list[str],
                em_scenarios: list[str]) -> xr.Dataset:
    '''Create the shifted IDF by using the Clausius-Clapeyron to project into the
    future based on emission scenarios of mean temperature.
    
    Parameters:
    -----------
    tempData : xarray.Dataset
        Dataset containing the temperature data to be used for the Clausius-Clapeyron
        equation
    ref_temp_data : xarray.Dataset
        Dataset containing the reference temperature data 
    IDF_files : List[strings]
        List of strings with the relative paths of the historical IDF files
    em_scenarios : List[strings]
        List of strings containing the emission scenarios being represented
    
    Returns:
    --------
    IDF_ds : xarray.Dataset
        Dataset containing the formatted IDF that has been shifted for each emission
        scenario
    '''
    # Initalize the function with lists that will hold the DataArrays
    da_list = []
    con_list = []
    lat_list = []
    lon_list = []
    ref_list = []
    stnName = []
    
    print("Shifting the IDF data based on input temperature")
    # Cycle through each IDF station file, and extract the information required
    for i, file in enumerate(tqdm(IDF_files)):
        # Initialize variable
        #mod_time_as_int=tempData.coords['time'].values.astype('datetime64[Y]').astype(int)+1970
        
        # Read in file
        dictIDF = read_ECCC_IDF(file)
        # Find temperature data
        temp = tempData.sel(dict(lat=dictIDF['location']['latitude'],
                            lon=dictIDF['location']['longitude']*-1),
                            method='nearest')
        rT=ref_temp_data['tg_mean'].sel(dict(lat=dictIDF['location']['latitude'],
                                    lon=dictIDF['location']['longitude']*-1.),
                                    method='nearest')
        """
        # Get mid-point of IDF period of record
        baseTime = int(np.mean((dictIDF['period']['start_date'],
                                dictIDF['period']['end_date'])))
        
        # Use mid-point to determine which 30yr period to use, subtact 15 from baseTime so that you choose
        # 30y period with baseTime in middle (there must be a better way)
        iBaseTime = np.argmin(abs(mod_time_as_int-(baseTime-15)))
        """
        # Calculate dTemp - broadcast to all models, emission scenarios, times
        dTemp = temp['tg_mean'] - rT
        dTemp.attrs['units'] = 'delta_degreeC' # Change units for Clausis Clapeyron equation
        
        # Find the baseline value to be used in xarray dataset
        # In the IDF files, missing values are filed with -99.9, here they are replaced
        pr_baseline = xr.DataArray(dictIDF['IDF_rates'].replace(-99.9, np.nan),
                                   coords=dict(duration=dictIDF['IDF_rates'].index,
                                               return_period=dictIDF['IDF_rates'].columns),
                                   attrs={"units":"mm/hr"})
        
        # Calculate the precip future using clausius clapeyron
        pr_future = xci.clausius_clapeyron_scaled_precipitation(dTemp, pr_baseline)
        pr_future = pr_future.assign_coords({'ssp': em_scenarios})
        
        # Grab the station ID
        stationID = dictIDF['location']['ID']
        
        # Set the daIDF to the furture precip at the correct station based on ID
        da_list.append(pr_future)
        
        # Add the interval confidence, latitude & longitude
        con_list.append(xr.DataArray(
            dictIDF['IDF_rate_confidence'],
            dims=('duration', 'return_period')).assign_coords(
                dict(station=stationID)
        ))
        lat_list.append(xr.DataArray(
            dictIDF['location']['latitude']
            ).assign_coords(
                dict(station=stationID)
        ))
        lon_list.append(xr.DataArray(
            dictIDF['location']['longitude']
            ).assign_coords(
                dict(station=stationID)
        ))
        
        # Add each stations reference period for later use
        ref_list.append(xr.DataArray(
           '1974 to 2005'
           ).assign_coords(
                dict(station=stationID)
        ))
        stnName.append(xr.DataArray(
            dictIDF['location']['name']
            ).assign_coords(
                dict(station=stationID)
        ))       
    
    # Combine each of the lists into one DataArray based on the 'station' dimmension
    daIDF = xr.concat(da_list, dim='station')
    conIDF = xr.concat(con_list, dim='station')
    latIDF = xr.concat(lat_list, dim='station')
    lonIDF = xr.concat(lon_list, dim='station')
    refIDF = xr.concat(ref_list, dim='station')
    stnNameIDF = xr.concat(stnName, dim='station')
    # Combine the IDF information into one Dataset
    IDF_ds = xr.Dataset(dict(
        IDF_data=daIDF,
        IDF_confidence=conIDF)).assign_coords(
            ref=refIDF, 
            station_name=stnNameIDF,
            lat=latIDF,
            lon=lonIDF)

    # Return the IDF_ds with the specification of the ssp370 attribute
    return IDF_ds
#%%
if __name__ == "__main__":
    # Set the emmision scenarios
    ssps = ['ssp126', 'ssp245', 'ssp370', 'ssp585']

    # Grab temperature data
    tempData = temperatureData_Download(ssps) 
    ref_temp_data = reftemperatureData_Download(ssps)
    # Load list containg paths of all IDF files
    IDF_files = glob(r'IDF-files/*/idf_*') 

    # Grab the historical data and format it
    histIDF = reformat_historical_IDF(IDF_files)    
    
    # Build the shifted IDF from the Temeprature data
    IDF_ds = IDF_Builder(tempData, ref_temp_data, IDF_files, ssps)

    # Perform the percentile calculations and assign the data_variables to the
    # IDF
    IDF_ds = IDF_ds.assign(calculate_percentiles(IDF_ds, split=True).assign(
        IDF_data_scaledp95 = percent95_IDFs(IDF_ds, histIDF, tempData, ref_temp_data)))

    # Assign Atrributes
    IDF_ds = IDF_ds.assign_attrs({'Units': 'mm/hr',
        'Description': 'Station based IDF data scaled with climate models',
        'NOTE': 'ssp370 is full of NaNs in models 25 & 26 (index: 24,25) as the climate models do not exist for that scenario'})

    print("Saving the projected IDF into desired path")

    # Check to see if an ouput path was provided
    if len(sys.argv) > 1:
        outputPath = os.path.join(sys.argv[1], 'national_IDF_projection_dataset_CMIP6_v4.nc')
    else:
        # If no provided path set default to current location
        outputPath = r'./national_IDF_projection_dataset_CMIP6_v2.nc'

    # Save to output Path and ignore the RuntimeWarning from xclim
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        IDF_ds.to_netcdf(outputPath)
        print(f'Saved the shifted IDF to {outputPath}')
