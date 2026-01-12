# !/bin/bash

# List all the Provinces and Territories
prov_terr_list=("AB" \
                "BC" \
                "MB" \
                "NB" \
                "NL" \
                "NS" \
                "NT" \
                "NU" \
                "PE" \
                "QC" \
                "ON" \
                "SK" \
                "YT")

# Cycle through the list and download each zip file 
echo "Downloading Province and Territory station IDF curves"
for prov in "${prov_terr_list[@]}"
do
    wget https://collaboration.cmc.ec.gc.ca/cmc/climate/Engineer_Climate/IDF/idf_v3-30_2022_10_31/IDF_Files_Fichiers/"$prov".zip
done

# Unzip all files using unzip (which may need to be downloaded)
echo "Unzipping the downloaded zip files"
for f in `ls ./*.zip`
do
    unzip -qq $f
done

# Remove all the excess and unnecessary files
echo "Removing excess files"
rm */*.png
rm */*.pdf
rm *.zip

echo "Finished Downloading IDF files"