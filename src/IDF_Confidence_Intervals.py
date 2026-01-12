########## IDF_Confidence_Intervals ##########
# This script contains code for calculating the required confidence intervals 
# for the scaled IDFs. This script includes two aspects:
#       1. Percentile Calculations
#       2. Scaling from the historical data
##############################################

# Import Required Libraries
import datetime, sys, warnings
import xarray as xr
from xclim.ensembles import ensemble_percentiles
import pandas as pd
import numpy as np
from tqdm import tqdm
# Import tools and custom functions
from src.Tools import next_nearest_grid
#%%
# Calculate the rainfall intensity based on historical reference and change in
# temperature
def future_rainfall_intensity(ref_I: float,
                              dTemp: float,
                              cc_adj: float = 1.07):
    """ Calculate the future rainfall intensity based off historical reference.
    Based on CSA standards on creating IDFs with a changing climate, equation 5.1
    
    Parameters
    ----------
    ref_I : float 
        Historical reference intensity of a duration and return period
    dTemp : float
        Projected change in temperature
    cc_adj : float, default=1.07
        Rainfall-Temperature scaling factor. Default value (1.07) set based to 
        CSA standards.
    
    Returns
    -------
    float
        The projected future rainfall intensity
    """
    return ref_I*(cc_adj)**dTemp
#%%
# Calculate the percentiles of the future IDF
def calculate_percentiles(da: xr.DataArray,
                          percentiles: tuple[int] = (10, 25, 50, 75, 90),
                          split: bool = False) -> xr.Dataset:
    """Generate from the historical IDFs new data variables containing the 
    calculated percentiles
    
    Parameters
    ----------
    da : xarray.DataArray
        A xarray dataset containing the dataset to find perceniles of
    percentiles : Tuple[integers]
        A tuple contianing the percentiles to be calculated  
    split : boolean, default=False
        Whether returned xarray.Dataset contains the same data variables and the 
        percentiles are included as coordinates (default). If true, returns separate
        data variables for each percentile.
        
    Returns
    -------
    xarray.Dataset
        Dataset containing ONLY the calculated percentiles of the future IDF
    """
    # Check if dimensions contain model or realization terminology
    if 'model' in da.dims:
        da = da.rename({'model':'realization'})

    return ensemble_percentiles(da, values=percentiles, split=split)
#%%
# Calculate the scaled uncertainty of the 95th percentile using the historical IDF
def scale_IDF_95th(histIDF: xr.Dataset,
                   tempData: xr.Dataset,
                   ref_temp_data: xr.Dataset,
                   em_scenario: str,
                   timeFut: str) -> xr.DataArray:
    """ Scale the historical IDF 95th confidence level based on change in 
    temperature. As is instructed in CSA W231 section 5.4.3
    
    Parameters
    ----------
    histIDF : xarray.Dataset
        Dataset containing the formatted historical IDF data for a single station. 
        See Tools.py for function to combine all IDFs into one dataset, then extract 
        each station into a single datarray.
    tempData : xarray.Dataset
        Dataset containing the modeled temperature data
    ref_temp_data : xarray.Dataset
        Dataset containing the reference temperature data
    em_scenario : str
        The emission scenario you would like to perform the scaling around
    timeFut : str
        Future date to pull for determining the range of local warming
    
    Returns
    -------
    xarray.DataArray
        DataArray contianing the scaled 95th confidence interval for given emission
        scenario, and time.
    """
    # Extract the coords for from the station
    stnLat = float(histIDF.lat.values)
    stnLon = float(histIDF.lon.values) * -1
    
    # Find the temperature data for the station
    stnTemp = tempData.sel(lat=stnLat, lon=stnLon, method='nearest').sel(ssp=em_scenario).load()
    stnrefTemp = ref_temp_data.sel(lat=stnLat, lon=stnLon, method='nearest').sel(ssp=em_scenario).load()

    if stnTemp.isnull().all():
        stnTemp = next_nearest_grid(tempData.to_dataset(), stnLat, stnLon).sel(ssp=em_scenario)
        stnrefTemp = next_nearest_grid(ref_temp_data, stnLat, stnLon).sel(ssp=em_scenario)
    # Calclate dTemp as the range of local warming between reference and future period
    # for this time and place
    dTemp = stnTemp.sel(time=timeFut) - stnrefTemp

    # Check to see if the dTemp is still empty, if so just return NaNs
    # Likely needed for station 8204708 on Sable Island, Nova Scotia
    if dTemp.tg_mean.isnull().all():
        print('Null!!!')
        # Grab input shape
        inputShape = tuple(histIDF.sizes[d] for d in ['duration', 'return_period'])
        # Create empty array to fill out the space for that year
        output = xr.DataArray(
            np.full(inputShape, np.nan),
            dims=('duration', 'return_period'),
            coords=dict(
                duration = histIDF.duration.values,
                return_period = histIDF.return_period.values,
                station = str(histIDF.station.values),
                ssp=em_scenario, time=timeFut))
    else:
        # Take the 75th quantile of the range
        dTemp_75th = calculate_percentiles(dTemp, [75], split=True)
        # Calculate the unscaled 95th histoircal IDF 
        histIDF_95th = histIDF['IDF_data'] + histIDF['IDF_confidence']

        # Calculate the future 95th interval via scaling and make it into an output array
        output = xr.DataArray(
            future_rainfall_intensity(histIDF_95th, dTemp_75th['tg_mean_p75']).values,
            dims=('duration', 'return_period'),
            coords=dict(
                station = str(histIDF.station.values),
                duration = histIDF.duration.values,
                return_period = histIDF.return_period.values,
                ssp=em_scenario, time=timeFut))

    return output
#%%
# Now cycle through the entirety of the shifted IDFs and calculate the scaled 95th
# for uncertainty
def percent95_IDFs(dsIDF: xr.Dataset,
                   histIDF: xr.Dataset,
                   tempData: xr.Dataset,
                   ref_temp_data: xr.Dataset,) -> xr.DataArray:
    '''Cycle through the shifted IDF and calculate the percentiles:
        - 10th, 25th, 75th, and 90th
        - The scaled 95th for dates in the future
    
    Parameters
    -----------
    dsIDF : xarray.Dataset
        The dataset containing the IDF_data to have added 
    hsIDF : xarray.Dataset
        Dataset containing the historical IDFs, see reformat_historical_IDFs() in
        tools for formatting
    tempData : xarray.Dataset
        Dataset containing the temperature data used
    reftempData : xarray.Dataset
        Dataset containing the ref temperature data used
    
    Returns
    -------
    xarray.DataArray
        DataArray containing the scaled 95th percentiles, with the stations, ssps, 
        and time as coordinates.
    '''
    print("Calculating the scaled 95th percentiles")
    
    # Create a function to check if year is in future
    isFuture = lambda year: pd.Timestamp(year).year > datetime.datetime.now().year

    # Compute and load the 'tg_mean' values in tempData for quicker access
    tempData_computed = tempData['tg_mean'].compute()

    daList = [] # Initialize an empty list to hold the DataArrays
    for stat in tqdm(dsIDF.station.values):
        # Grab station name
        for emScen in dsIDF.ssp.values:
            for t in dsIDF.time.values:
                # Check the year and if false fill with NaNs instead
                if not isFuture(t):
                    # Grab input shape
                    inputShape = tuple(dsIDF.sizes[d] for d in ['duration', 'return_period'])
                    # Create empty array to fill out the space for that year
                    output = xr.DataArray(
                        np.full(inputShape, np.nan),
                        dims=('duration', 'return_period'),
                        coords=dict(
                            duration = dsIDF.duration.values,
                            return_period = dsIDF.return_period.values,
                            station = stat, ssp=emScen, time=t))
                else:
                    # Grab the specific historical period
                    histDS = histIDF.sel(station=stat)
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', RuntimeWarning)
                        output = scale_IDF_95th(histDS, tempData_computed, ref_temp_data, emScen, t).assign_coords(
                            dict(time=t))
                daList.append(output)
                    
    # Combine all of the arrays in the list into one dataArray
    combined = xr.concat(daList, dim='z') # Temp dimmesnion z
    
    # Unstack the z-dim in the combined array based off station, ssp, and time
    return combined.set_index(z=['station', 'ssp', 'time']).unstack('z')
