# Script used to save an IDF dataset into station based CSVs

# Import Libraries
import os, sys, shutil
from glob import glob
from tqdm import tqdm
import pandas as pd
import numpy as np
import xarray as xr
import sigfig
from math import log10, floor

# Import custom functions
from src.Tools import reformat_historical_IDF


#%%
# Function to cycle through the stations and save one full folder and one QS per station
def cycle_stations_csv(dsIDF, emScens, dirPath, histDS=None):
    # Cycle through station IDs

    for stn in tqdm(dsIDF.station.values.tolist()):
        sname = dsIDF.sel(station=stn).station_name.item()
        sLat = dsIDF.sel(station=stn).lat.item()
        sLon = dsIDF.sel(station=stn).lon.item()
        # Check if directory has the station in it already and if not make folder
        dirStn = os.path.join(dirPath,'output', 'CMIP6', f'{sname}_{stn}_{sLat:.1f}_{sLon:.2f}-cmip6')
        dirStnQS = os.path.join(dirPath,'output', 'CMIP6_QuickStart', f'{sname}_{stn}_{sLat:.1f}_{sLon:.2f}-cmip6-quickstart')
        if not os.path.isdir(dirStn):
            os.mkdir(dirStn)
            # Copy the readme files in here
            shutil.copyfile(dirPath+'ReadMe-IDFs-EN.pdf', dirStn+'/ReadMe.pdf')
            shutil.copyfile(dirPath+'ReadMe-IDFs-FR.pdf', dirStn+'/LisezMoi.pdf')

        # Cycle through each emissions scenario
        for em in emScens:
            station_emScen_df(stn, em, dsIDF, dirStn, histDS=histDS)

        #copy into quick start, cut up and zip
        shutil.copytree(dirStn, dirStnQS)

        # Create target folders if they don't exist
        for year in ["2051", "2071"]:
            os.makedirs(os.path.join(dirStnQS, year), exist_ok=True)
        
        # Move matching files
        for src in ["ssp245", "ssp585"]:
            src_path = os.path.join(dirStnQS, src)
        
            if not os.path.isdir(src_path):
                continue
        
            for fname in os.listdir(src_path):
                for year in ["2051", "2071"]:
                    if year in fname:
                        src_file = os.path.join(src_path, fname)
                        dst_file = os.path.join(dirStnQS, year, fname)
        
                        # Move file
                        shutil.move(src_file, dst_file)
                        break  # avoid double-moving
        
        # Remove ssp folders once empty
        for src in ssps:
            src_path = os.path.join(dirStnQS, src)
            if os.path.isdir(src_path):
                shutil.rmtree(src_path)
        #zip QS file
        shutil.make_archive(dirStnQS, 'zip', dirStnQS)
        shutil.rmtree(dirStnQS)
        #zip full file in CMIP6 fld
        shutil.make_archive(dirStn, 'zip', dirStn)
        shutil.rmtree(dirStn)


#%%
# Function that takes in a single station and emmission scenario and outputs the
# files to be saved
def station_emScen_df(
    stn,
    emScenario,
    ds,
    dirPath,
    percs={
        'p50': 'median',
        'p10': '10th_percentile',
        'p25': '1st_quartile',
        'p75': '3rd_quartile',
        'p90': '90th_percentile',
        'scaledp95': 'scaled_95th_confidence_limit'
    },
    histDS=None
):
    """
    Write station IDF data to CSV.

    """

    # ------------------------------------------------------------
    # HISTORICAL (UNCHANGED)
    # ------------------------------------------------------------
    if emScenario == 'historical':
        df = pd.DataFrame()

        for rp in histDS.return_period.values.tolist():
            dHist = histDS.sel(station=stn, return_period=rp)['IDF_data']
            dHist_CI = histDS.sel(station=stn, return_period=rp)['IDF_confidence']

            tmp = [np.round(x, 1) for x in dHist.values]
            tmp.extend([np.round(x, 1) for x in dHist_CI.values])
            df[rp] = tmp

        durations = histDS.duration.values.tolist()
        durations.extend([x + "_95%_confidence_limit" for x in durations])
        df.insert(0, "Duration", durations, True)

        sName = histDS.sel(station=stn).station_name.item()
        sLat = histDS.sel(station=stn).lat.item()
        sLon = histDS.sel(station=stn).lon.item()

        outFile = (
            f'{dirPath}/{sName}_{stn}_{sLat:.2f}_{sLon:.2f}_{emScenario}.csv'
        )

        df.to_csv(outFile, index=False)

    # ------------------------------------------------------------
    # FUTURE SCENARIOS – VERTICAL FORMAT + METADATA
    # ------------------------------------------------------------
    else:
        dirEm = os.path.join(dirPath, emScenario)
        if not os.path.isdir(dirEm):
            os.mkdir(dirEm)

        years = list(range(2011, 2072, 10))

        for year in years:
            time_sel = f'{year}-01-01'
            rows = []

            # Build vertical table
            for p, pn in percs.items():
                for i, dur in enumerate(ds.duration.values.tolist()):
                    row = {
                        "Duration": dur,
                        "Percentile": pn
                    }

                    for rp in ds.return_period.values.tolist():
                        da = ds.sel(
                            station=stn,
                            time=time_sel,
                            ssp=emScenario,
                            return_period=rp
                        )[f'IDF_data_{p}']

                        val = da.values[i]
                        if abs(val) >= 10:
                            row[rp] = int(round(val))
                        else:
                            row[rp] = round(val, 1)

                    rows.append(row)

            df = pd.DataFrame(rows)

            # ---- metadata ----
            futYear = year + 29
            sName = ds.sel(station=stn).station_name.item()
            sLat = ds.sel(station=stn).lat.item()
            sLon = ds.sel(station=stn).lon.item()

            outFile = (
                f'{dirEm}/{sName}_{sLat:.2f}_{sLon:.2f}_'
                f'{emScenario}_{year}-{futYear}.csv'
            )

            metadata = [
                f"# Station Name: {sName}",
                f"# Station ID: {stn}",
                f"# Latitude: {sLat:.2f}",
                f"# Longitude: {sLon:.2f}",
                f"# Emissions Scenario: {emScenario}",
                f"# Period: {year}-{futYear}",
                ""
            ]

            # Write metadata + data
            with open(outFile, "w", newline="") as f:
                for line in metadata:
                    f.write(line + "\n")
                df.to_csv(f, index=False)
#%%
if __name__ == "__main__":
    
    dirPath = os.getcwd()
    # Lay out the emmision scenarios
    ssps = ['historical', 'ssp126', 'ssp245', 'ssp370', 'ssp585']

    # Read in the historical IDF files
    histIDF_ds = reformat_historical_IDF(glob(r'IDF-files/*/idf_*'))

    # Read in the new IDF dataset
    inputPath = os.path.join(dirPath, 'national_IDF_projection_dataset_CMIP6_v4.nc')
    newIDF_ds = xr.open_dataset(inputPath).fillna(-99.9)

    # Convert the NetCDF into csv for each station
    print('Saving the IDF data into station based folders with CSVs')
    cycle_stations_csv(newIDF_ds, ssps, dirPath, histDS=histIDF_ds)
