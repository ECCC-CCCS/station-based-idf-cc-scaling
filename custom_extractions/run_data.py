#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 22:08:38 2025

@author: evg000
"""

from GCM_extract import *
from CDca_extract import *
from CDca_per_delta_extract import *
from CMIP6_drought_extract import *
from FWI_extract import *
from SLR_extract import *
from functions import *
import sys
sys.path.append(os.path.expanduser('~/scratch/'))
from filepaths import cspaths
import argparse

directory = cspaths.workspace

GCM_ocean_variables = ['dissic','tos','sos','talk','ph']
GCM_atmos_variables = ['siconc','sithick','sfcWind']
drought_indices = ['SPEI', 'SRI_surface', 'SSI_total', 'SSI_surface', 'mrro', 'mrros', 'mrsos', 'mrso'] # other options: 'SRI_total'

ETCCDI_variables = ['tn_mean', 'tn_min', 'tg_mean', 'tx_mean', 'tx_max', 
                    'cdd', 'dlyfrzthw_tx0_tn-1','frost_days', 'frost_free_season',
                    'gddgrow_0', 'gddgrow_5', 'ice_days', 'nr_cdd', 'prcptot', 'prsntot', 'r10mm', 'r1mm', 'r20mm',
                    'rx1day','rx5day','snowfall_season_length', 'tnlt_m15', 'txgt_25', 'txgt_30']
    
ETCCDI_variables_percent = ['cdd', 'dlyfrzthw_tx0_tn-1','frost_days', 'frost_free_season',
                            'gddgrow_0', 'gddgrow_5', 'ice_days', 'nr_cdd', 'prcptot', 'prsntot', 'r10mm', 'r1mm', 'r20mm',
                            'rx1day','rx5day','snowfall_season_length', 'tnlt_m15', 'tnlt_m25', 'txgt_25','txgt_30']
  
# other options (% and abs change): 'ccdcold_18', 'hddheat_18', 'sn10mm','sn2mm', 'snx1day', 'tnlt_m25','tr_18','tr_20', 'tr_22', 'txgt_27', 'txgt_29', 'txgt_32'
# other options (abs change only):     'first_fall_frost','last_spring_frost', 'last_snowfall'  
  
FWI_variables = ['BUIp95','FWIp95','fire_season_length']  

rcps = ['RCP26', 'RCP45', 'RCP85'] 
ssps = ['ssp126', 'ssp245', 'ssp370','ssp585'] 
periods = ['1981_2010', '2011_2040', '2041_2070', '2071_2100']


## SHEETS MUST BE FORMATTED PROPERLY: No stations with data across multiple lines
## Site ID column must be called "FederalSiteIdentifier"
sheet_names = ['FCSAP_template_Jul23.csv']

def pull_data(GCM_atmos = False,
              GCM_ocean = False,
              FWI = False,
              RSLC = False,
              drought = False,
              CDca = False,
              CDca_percent = False,
              ssp=None,
              rcp=None):
        
    if GCM_atmos:
        extract_GCM(GCM_atmos_variables, 'atmos', ssp, periods, sheet_names)
        print(f'GCM atmos completed for {sheet_names}. Variables: {GCM_atmos_variables}, SSP: {ssp}')
        
    if GCM_ocean:
        extract_GCM(GCM_ocean_variables, 'ocean', ssp, periods, sheet_names)
        print(f'GCM ocean completed for {sheet_names}. Variables: {GCM_ocean_variables}, SSP: {ssp}')
    
    if FWI:
        extract_FWI(FWI_variables, rcp, periods, sheet_names)
        print(f'FWI completed for {sheet_names}. Variables: {FWI_variables}, RCP: {rcp}')
    
    if RSLC:
        extract_SLC(ssp, sheet_names)
        print(f'SLC completed for {sheet_names}. Variables: SLR, SSP: {ssp}')
    
    if drought:
        extract_drought(ssp, periods, sheet_names, drought_indices)
        print(f'Drought indices completed for {sheet_names}. Variables: {drought_indices}, SSP: {ssp}')
    
    if CDca_percent:
        extract_CDca_percent(ETCCDI_variables_percent, ssp, periods, sheet_names)
        print(f'ClimateData.ca CDDCIC percent change indices completed for {sheet_names}. Variables: {ETCCDI_variables_percent}, SSP: {ssp}')
    
    if CDca:
        extract_CDca(ETCCDI_variables, ssp, periods, sheet_names)
        print(f'ClimateData.ca CDDCIC indices completed for {sheet_names}. Variables: {ETCCDI_variables}, SSP: {ssp}')
        
     



for ssp in ssps:
  pull_data(#GCM_atmos = True,
            #GCM_ocean = True,
            #RSLC = True,
            drought = True,
            #CDca_percent = True,
            #CDca = True,
            ssp=ssp)
            
#for rcp in rcps:
#  pull_data(FWI = True, rcp=rcp)

'''

parser = argparse.ArgumentParser(description='Extract data with specified options')
parser.add_argument('--gcm_atmos', action='store_true')
parser.add_argument('--gcm_ocean', action='store_true')
parser.add_argument('--fwi', action='store_true')
parser.add_argument('--rslc', action='store_true')
parser.add_argument('--spei', action='store_true')
parser.add_argument('--cdca', action='store_true')

parser.add_argument('--ssp', choices=['ssp126', 'ssp245', 'ssp370', 'ssp585'])
parser.add_argument('--rcp', choices=['RCP26', 'RCP45', 'RCP85'])

# Parse arguments
args = parser.parse_args()

pull_data(
        GCM_atmos=args.gcm_atmos,
        GCM_ocean=args.gcm_ocean,
        FWI=args.fwi,
        RSLC=args.rslc,
        SPEI=args.spei,
        CDca=args.cdca,
        ssp=args.ssp,
        rcp=args.rcp
    )'''
