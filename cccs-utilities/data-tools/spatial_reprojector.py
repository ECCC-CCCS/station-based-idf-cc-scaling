"""Project from latlon coordinates to grid (meter/meter), or vice versa.

Notes:
-Utility functions are provided for both for projection in both directions.
-Lat/lon is hardcoded to WGS84 datum - change this as needed.
-If you're working with something else, use the appropriate EPSG code.
-Be careful to check that the xy outputs make sense are in expected order, before using!

Inputs: 
-lat/lon or x/y values (should work with scalars, vectors, arrays..?)
-Coordinate Reference System (CRS), see pyproj.Transformer documentation for more

Outputs:
-projected x/y or lat/lon values
"""
from pyproj import Transformer

def latlon2grid(lat,lon,output_projection_crs):
    transformer=Transformer.from_crs('EPSG:4326',output_projection_crs)
    x,y = transformer.transform(xx=lat,yy=lon)
    return x,y
    
def grid2latlon(x,y,input_projection_crs):
    transformer=Transformer.from_crs(input_projection_crs,'EPSG:4326')
    lat,lon = transformer.transform(xx=x,yy=y)
    return lat,lon
             
def main():
    #Dummy calls - can modify for real use if required
    return latlon2grid(lat_in,lon_in,source.crs)
    return grid2latlon(x_in,y_in,source.crs)

if __name__ == "__main__":
    main()
      