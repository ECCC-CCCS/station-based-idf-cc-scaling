import sys
import os
sys.path.append(os.path.expanduser('~/scratch/'))
from filepaths import cspaths
import subprocess
import xarray as xr
import glob
import datetime
import gc
import xclim
from xclim import ensembles

gcm_type = 'ocean' #or atmos

def get_model(path):
    return(os.path.basename(path).split("_")[2])

def prep(ds):
    mod = get_model(ds.encoding['source'])
    ds = ds.assign_coords(dict(model=mod)).expand_dims('model')
    ds = ds.convert_calendar('noleap', align_on='year')
    
    #normalize the data to have same day/hour for every monthly value
    new_time = xr.cftime_range(
    start=f'{ds.time.values[0].year}-{ds.time.values[0].month:02d}-01 00:00:00',
    periods=len(ds.time),
    freq='MS')

    # Update the time coordinate in the dataset
    ds['time'] = new_time
    
    ds = ds.convert_calendar('noleap', align_on='year')

    if "olevel" in ds.coords:
        ds = ds.rename({"olevel": "lev"})
        
    if "lev" in ds.coords:
        ds = ds.drop_vars("lev")
    
    return ds

def add_attrs(ds, rcp, p, hist_files, proj_files, qt, model_num):
    ds.attrs['input_data_files'] = [os.path.basename(fl) for fl in hist_files + proj_files]
    ds.attrs['rcp'] = rcp          
    ds.attrs['period_of_climatological_mean'] = pers[p]
    ds.attrs['description'] = f'Multi-model percentile {qt} ({model_num} models) of 30-year means for specified period, from monthly means.'
    ds.attrs['generation_date'] = f"{datetime.datetime.now():%Y-%m-%d}"
    ds.attrs['generated_by'] = 'Eva Gnegy, CCCS-ECCC'
    #ds.attrs['github_version'] = 'https://github.com/ECCC-CCCS/custom-extractions/commit/' + subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    ds.attrs['script_name'] = sys.argv[0]
    return ds

ssps = ['ssp126', 'ssp245', 'ssp370', 'ssp585'] #if adding or removing one, edit get_models_inclusive function accordingly

quantiles = [0.1, 0.5, 0.9]

pers = dict(pr = ('1981', '2010'),
            pr2 = ('1976', '2005'),
            p1 = ('2011', '2040'), 
            p2 = ('2041', '2070'),
            p3 = ('2071', '2100') 
            )

all_years = [int(year) for period in pers.values() for year in period]

# Get the minimum and maximum years
min_year = min(all_years)
max_year = max(all_years)

chunks = {'model': -1}

if gcm_type == 'ocean':
    variables = ['dissic','ph','talk','sos','tos'] 
    directory = cspaths.CMIP6_GCM_ocean
    add_fp = 'regridded'
    
elif gcm_type == 'atmos':
    variables = ['siconc', 'sithick', 'snd','sfcWind', 'snd']
    directory = cspaths.CMIP6_GCM_atmos
    add_fp = ''
    

# returns set of models that exists for all 4 runs for given variable
def get_models_inclusive(var):
    hist_files = glob.glob(f'{directory}{var}/{add_fp}/*historical*')
    ssp126_files = glob.glob(f'{directory}{var}/{add_fp}/*ssp126*')
    ssp245_files = glob.glob(f'{directory}{var}/{add_fp}/*ssp245*')
    ssp370_files = glob.glob(f'{directory}{var}/{add_fp}/*ssp370*')
    ssp585_files = glob.glob(f'{directory}{var}/{add_fp}/*ssp585*')

    models_hist = {get_model(path) for path in hist_files}
    models_ssp126 = {get_model(path) for path in ssp126_files}
    models_ssp245 = {get_model(path) for path in ssp245_files}
    models_ssp370 = {get_model(path) for path in ssp370_files}
    models_ssp585 = {get_model(path) for path in ssp585_files}

    if gcm_type == 'atmos':
        return models_hist & models_ssp126 & models_ssp245 & models_ssp370 & models_ssp585
    elif gcm_type == 'ocean':
        return models_hist & models_ssp126 & models_ssp245 & models_ssp585


for var in variables:
    
    models_inclusive = get_models_inclusive(var)
    model_num = f'{len(models_inclusive)}'
    
    print(var)
    print(model_num)
#%%
    for ssp in ssps:
        print(ssp)
        
        if var == "sithick":
            hist_files_all = glob.glob(f'{directory}{var}/{add_fp}/*historical*1900*')
        else:
            hist_files_all = glob.glob(f'{directory}{var}/{add_fp}/*historical*')
            
        proj_files_all = glob.glob(f'{directory}{var}/{add_fp}/*{ssp}*')
        
    
        # only select models that exist for all runs (historical + all desired ssps)
        hist_files = sorted([path for path in hist_files_all if get_model(path) in models_inclusive])
        proj_files = sorted([path for path in proj_files_all if get_model(path) in models_inclusive])
      
        # this model for this var has 2 versions of the grid
        if var == "sithick":
            for file in proj_files:
                if '_gn_' in file and 'GFDL-ESM4' in file:
                    proj_files.remove(file)
        
        #hist = xr.open_mfdataset(hist_files, preprocess=prep)[var]
        #proj = xr.open_mfdataset(proj_files, preprocess=prep)[var]
    
        # allows for some files to have more years, open_mf throws an error when not all files have exact timeframes
        hist_indv = [prep(xr.open_dataset(file).sel(time=slice(f'{min_year}', f'{max_year}'))[var]) for file in hist_files]
        hist = xr.concat(hist_indv, dim='model')

        proj_indv = [prep(xr.open_dataset(file).sel(time=slice(f'{min_year}', f'{max_year}'))[var]) for file in proj_files]
        proj = xr.concat(proj_indv, dim='model')
        
 
        data = xr.merge([hist, proj], combine_attrs='drop_conflicts')


        for p in pers.keys():
              print(pers[p])
              dat = data.sel(time=slice(*pers[p])).mean(dim='time').chunk(chunks)

              for qt in quantiles:
                  out = dat.quantile(qt, dim='model',keep_attrs=True)
                  
                  encoding = {var: {'dtype': 'float32', 'zlib': True}}
                  out = add_attrs(out, ssp, p, hist_files, proj_files, qt, model_num)
                  out.to_netcdf(f'{cspaths.workspace}/{var}_{ssp}_{pers[p][0]}_{pers[p][1]}_{qt}_pctl_CMIP6_{model_num}GCM.nc', encoding=encoding)
                  
                  del(out)
                  gc.collect()

              del(dat)
              gc.collect()
    
        del([hist, proj, data])
        gc.collect()