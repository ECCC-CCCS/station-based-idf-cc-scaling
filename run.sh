#!/bin/bash
# Script to run the needed files

OUTPATH="/gpfs/fs7/eccc/cccs/jcg010/IDF/"

# Call the script to make the netcdf ~15mins
python -m src.IDF_Shifting "$OUTPATH"

# Call script to convert netcdf into csv ~30mins
python -m src.IDF_csv "$OUTPATH"