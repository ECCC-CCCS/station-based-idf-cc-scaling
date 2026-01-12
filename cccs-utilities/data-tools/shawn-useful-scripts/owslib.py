import owslib
import pandas as pd 
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from owslib.wcs import WebCoverageService
from owslib.wps import WebProcessingService
from owslib.csw import CatalogueServiceWeb
from owslib.sos import SensorObservationService
from owslib.waterml.wml11 import WaterML_1_1
from owslib.wmts import WebMapTileService
from owslib.wms import WebMapService



#wms = WebMapService('https://climate-change.canada.ca/climate-data/#/daily-climate-data')

wms = WebMapService('https://geo.weather.gc.ca/geomet/?lang=en&service=WMS&request=GetCapabilities', timeout=500)
                
#wms = WebMapService('http://wms.jpl.nasa.gov/wms.cgi', version='1.1.1')

wms.identification.type
wms.identification.version
wms.identification.title
wms.identification.abstract


#real operations:
print('Contents: '), list(wms.contents)
contents=list(wms.contents)

print('Operations:'),[op.name for op in wms.operations]

wms.identification.keywords

#########################

wms = WebMapService("""https://geo.weather.gc.ca/geomet/?lang=en&service=WMS&
                    request=GetCoverage&COVERAGE=GDPS.ETA_NT&BBOX=(-160,40,-30,80)
                    &CRS=EPSG:4326&WIDTH=560&HEIGHT=900&FORMAT=GeoTIFF_16""", timeout=500)


wms = WebMapService("""https://geo.weather.gc.ca/geomet/features/collections/climate-daily/items?
time=1840-03-01%2000:00:00/2019-11-02%2000:00:00&STN_ID=6839&sortby=PROVINCE_CODE,
STN_ID,LOCAL_DATE&f=csv&limit=150000&offset=0""")


wms = WebMapService("""https://geo.weather.gc.ca/geomet/features/collections/climate-daily/""")
# =============================================================================
# 
# https://geo.weather.gc.ca/geomet/features/collections/climate-daily/items?time=1840-03-01%2000:00:00/2019-11-02%2000:00:00
# &STN_ID=2939&sortby=PROVINCE_CODE,STN_ID,LOCAL_DATE&f=csv&limit=150000&offset=0
# =============================================================================

csv = WebMapService("""https://geo.weather.gc.ca/geomet/?lang=en&service=WMS&
                    request=/features/collections/climate-daily/items?
                    time=1840-03-01%2000:00:00/2019-11-02%2000:00:00&STN_ID=6839&sortby=PROVINCE_CODE,
                    STN_ID,LOCAL_DATE&f=csv&limit=150000&offset=0""", timeout=500)


wms = WebMapService("""https://geo.weather.gc.ca/geomet/?lang=en&service=WMS&
                    request=https://geo.weather.gc.ca/geomet/features/collections/climate-daily/items
                    ?time=1840-03-01%2000:00:00/2019-11-02%2000:00:00
                    &STN_ID=2939&sortby=PROVINCE_CODE,STN_ID,LOCAL_DATE&f=csv&limit=150000&offset=0""", timeout=500)

