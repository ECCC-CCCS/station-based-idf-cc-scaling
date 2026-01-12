'''
Code example for setting up a Bokeh plot and saving it to HTML file.
-> This plot provides a zoomable underlay map, and also drops some points on this map.
-> I tried to write the main placeholder variables are written in UPPERCASE
-> For better map presentations, it might be worthwhile to move to geoviews, which can use Bokeh as a backend (http://geoviews.org/)
-> For more, explore Bokeh documentation (https://docs.bokeh.org/en/latest/) 
'''

from bokeh.plotting import figure, output_file, save, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
from bokeh.models import ColorBar,ColumnDataSource,OpenURL,TapTool
from bokeh.palettes import YlOrRd9
from bokeh.transform import linear_cmap
from bokeh.models.tools import HoverTool
from bokeh.layouts import column, gridplot

from pyproj import Proj, transform

html_file_name="HTML_OUTPUT_NAME"

bbox_lat=[41.,71.] #bounding box for Canada.
bbox_lon=[360.-142.,360.-51.] #bounding box for Canada (note use of 0-360 range for longitude)
proj1 = Proj('epsg:4326', preserve_units=False) #lat/lon
proj2 = Proj('epsg:3785', preserve_units=False) #Mercator (which is apparently the default for bokeh maps

bbox_lat=[LOWER_LAT,UPPER_LAT] #decimal degrees
bbox_lon=[WESTERN_LON,EASTERN_LON] #decimal degrees, use 0 to 360 range (not -180 to 180)
bbox_x,bbox_y=transform(proj1,proj2,bbox_lat,bbox_lon) #convert these degrees into projection coordinates

tile_provider = get_provider(CARTODBPOSITRON) #Set the map provider.  CARTODBPOSITRON is just one of several providers of zoomable map underlays.

TOOLS='hover,pan,wheel_zoom,tap,lasso_select' #set of tools that are enabled on the final Bokeh plot.  There's lots of tools available...

#Set of info that appears when you hover over a point on the map.  '@' syntax is used to refer to a field from the 'source' dictionary
TOOLTIPS = [('LABEL1','@FIELD_NAME1'),
            ('LABEL2','@FIELD_NAME2'),
            ('LABELN','@FIELD_NAMEN'),
           ]

point_data=DATA #Data defining the Seems like it can be a numpy array, pandas, etc.

lats=DATA_POINT_LATITUDES
lons=DATA_POINT_LONGITUDES
name=DATA_POINT_LOCATION_NAME
x,y=transform(proj1,proj2,lats,lons) #convert from lat/lon to projected x,y units


source = ColumnDataSource(data={ #Package all the data to be used in the plot (either as plot points, color references, labels, etc.) here
              'x_values':x,
              'y_values':y,
              'FIELD_NAME1':point_data,
              'FIELD_NAME2':OTHER_DATA1,   
              'FIELD_NAMEN':OTHER_DATAN,
              'name':name
              })

palette=YlOrRd9[::-1] #A reference Bokeh color palette.  There's lots more...
mapper = linear_cmap(field_name=FIELD_NAMEN, palette=palette ,low=MIN_COLOR ,high=MAX_COLOR) #set the color map for points, and point to the actual data field 

p1.circle(x="x_values", y="y_values", source=source, size=10, fill_color=mapper, color='black', fill_alpha=0.8) #Draw actual points.  Note, the x, y arguments are the names of fields, in the 'source' object (which itself is identified in the source=source statement)

color_bar = ColorBar(color_mapper=mapper['transform'], width=8)
p1.add_layout(color_bar, 'right')
taptool = p1.select(type=TapTool) #This defines an object that responds to a tap on a point
taptool.callback = OpenURL(url='https://hpfx.collab.science.gc.ca/~***REMOVED***/FWI/@name.png') #tha specific action in this case is to open a new tab, with an URL to a station-specific plot (the name of which expands via '@name' thingie)

save(p) #this generates a standalone html file with the Bokeh plot.  You can put it anywhere you want.