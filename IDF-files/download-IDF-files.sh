#!/bin/bash

#Get all ECCC IDF files for all locations.  Google Drive file IDs obtained by looking at shared link URLs for each province.

#requires gdown, which was installed via pip into 3.8 python environment (even tho it's not a Python tool I think)

google_file_ids=("15eOgNs7O78esPguQxsmbhpMEgWfwTqzT" \
                 "10c-LqmEkHtFeGiyArgHAqUa4clYjhtVu" \
                 "1fdEEYCrj_t3Y3IXSXAALEUX-Urh2x5jG" \
                 "1HueZnQA398ESGi-1op34maE7NZAi2grk" \
                 "1V-8QENwq6yVSOfqErwn2Gm4NEyvmaoPx" \
                 "1pkwSW3sqGwRPBVw7Lzb3xGg2IZPbCzAV" \
                 "1iiOTzQe9f6sJnXaG-6xBrhGMMoPvL2Tw" \
                 "1OCpnA28Kk6F6MABvWzV2jPuDH2eMaoSx" \
                 "1VD_iqnFFO9SJ1mrll1Lj7yGuz-WURkfz" \
                 "1qEyLZaSksJ6I784jllO2cVF8csCe64Jo" \
                 "1XhloivDGWrl_x-yVxq6-qOFm7Lg9R3Rh" \
                 "1eY7rtbxdyGHhySInf77lW6RcVVjEmimL" \
                 "1eY7rtbxdyGHhySInf77lW6RcVVjEmimL" \
                 "1Don0TDvJ7oc_GkEGnSMl5LLHn737vDnN")
#for id in "${google_file_ids[@]}"; do
#    gdown https://drive.google.com/uc?id="$id"
#done

#for f in `ls ./*.zip`; do
#    unzip $f
#done

rm */*.png
rm */*.pdf

rm *.zip
