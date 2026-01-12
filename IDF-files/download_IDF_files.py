# Script for downloading all the Station IDF data
# Written in python so it is uable in both Mac, Linux, and Windows

# Import Libraries
import os
from glob import glob
import zipfile
import requests
from tqdm import tqdm

def downloadZips(prov_terr_list: list):
    # Function used to download all the provincial and territory zip files containing the IDF files
    print("Downloading Province and Territory station IDF curves")
    for prov in tqdm(prov_terr_list):
        url = f"https://collaboration.cmc.ec.gc.ca/cmc/climate/Engineer_Climate/IDF/idf_v3-30_2022_10_31/IDF_Files_Fichiers/{prov}.zip"
        
        r = requests.get(url)
        with open(f"{prov}.zip", 'wb') as f:
            f.write(r.content)


def unzipFiles(prov_terr_list):
    # Unzip all the files downloaded
    print("Unzipping all files")
    for prov in tqdm(prov_terr_list):
        with zipfile.ZipFile(f"{prov}.zip", 'r') as zip_ref:
            zip_ref.extractall()

def removeFiles():
    # Remove all excess files from the Provinces and Territories directories 
    print("Removing excess files")
    # Grab all files to remove
    files = glob("*/*.png") + glob("*/*.pdf") + glob("*.zip")
    for file in tqdm(files):
        os.remove(file)

def main():
    # Setup the list of provinces and territories to download
    prov_terr_list = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'PE', 'QC', 'ON', 'SK', 'YT']

    currWD = os.getcwd()
    # Check if the current directory is in  the IDF-files, change if not
    if os.path.basename(os.path.normpath(currWD)) != 'IDF-files':
        os.chdir('IDF-files')
    
    # Download all files
    downloadZips(prov_terr_list)

    # Unzip all the downloaded zip files
    unzipFiles(prov_terr_list)

    # Remove excess files
    removeFiles()

    # Change back to original directory
    os.chdir(currWD)

main()