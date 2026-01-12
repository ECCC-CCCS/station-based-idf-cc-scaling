from netCDF4 import Dataset
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib  as mpl
import glob, os
import time

def mf1(data):
    """ This function will only print the first digit after the point of the number put as input
    data=the floating point number 
    """
    return (float('{:.1f}'.format(data)))

def mf2(data):
    """ This function will only print the first 2 digits after the point of the number put as input
    data=the floating point number 
    """
    return (float('{:.2f}'.format(data)))

def Arctic_figure(input,fld,varName,tCentral,output, imgout, matrice_col=None, reverse_col=None, txtLabel=None,clevs=None):
    """ This function will open an 2D netcDF file, and make a 2D plot over Arctic for the desired variable.
    The function supposes that the file has the spatial dimensions noted with lat and lon.
    input = put here the path to the directory containing the netCDF file
    fld= put here the name of the netCDF file
    varName= put here the name of the variable contained in the netCDF file that you want to plot
    tCentral= put here the title of the figure, for example the name of the netCDf file
    output= put here the path and the name of the directory where the figure will be saved
    imgout = put here the name of the figure you want to save
    txtLabel= put here the string to plot on the color bar if wanted; if not wanted, 
    don't put this variable when you call the function
    clevels= put here an array with the values you want to use for the colorbar; 
    if nothing mentioned, the function will chose an array centered to zero with symmetrical limits defined by the greatest absolute value.
    matrice_col=  put here the array containing the code for colors to use similar to that presented in the function;
    if nothing mentioned, the function will chose a red to blue scale, with white values at center.
    reverse_col=do not mention this variable when you call the function if you don't want to reverse the order of colors,
    or put 'YES' if you want to reverse the order of colors
    """
    if matrice_col is None:
        matrice_col=[(0.0, 0.070588235294117674, 0.28627450980392155),
                                        (0.0, 0.14117647058823535, 0.4274509803921569),
                                        (0.0, 0.21176470588235285, 0.47450980392156861),
                                        (0.0, 0.35882352941176465, 0.5725490196078431),
                                        (0.0, 0.42941176470588238, 0.61960784313725492),
                                        (0.14117647058823524, 0.57058823529411762, 0.71372549019607845),
                                        (0.26013072828451794, 0.65098041296005249, 0.80000001192092896),
                                        (0.34117648005485535, 0.72156864404678345, 0.81568628549575806),
                                        (0.52941177090009051, 0.81777778863906858, 0.75294119119644165),
                                        (0.70588237047195435, 0.88496732711791992, 0.73071897029876709),
                                        (0.83137255907058716, 0.93411765098571775, 0.80705883502960207),
                                        [ 1.        ,  1.0,  1.0],
                                        [ 0.99607843,  0.87843137,  0.82352941],
                                        [0.99, 0.8, 0.7],
                                        [ 0.98823529,  0.73333333,  0.63137255],
                                        [ 0.98823529,  0.57254902,  0.44705882],
                                        [ 0.98431373,  0.41568627,  0.29019608],
                                        [ 0.9372549 ,  0.23137255,  0.17254902],
                                        [ 0.79607843,  0.09411765,  0.11372549],
                                        [ 0.64705882,  0.05882353,  0.08235294],
                                        [0.5, 0., 0.06],
                                        [ 0.40392157,  0.        ,  0.05098039],
                                        [0.2783814132520015, 0.0, 0.0]]
        if reverse_col is None:
            colors = mpl.colors.ListedColormap (matrice_col)
        else:
            colors = mpl.colors.ListedColormap (np.flip(matrice_col,0))
    nc = Dataset(input + fld)
    lats0 = nc.variables['lat'][:]
    lons0 = nc.variables['lon'][:]
    lons0, lats0 = np.meshgrid(lons0, lats0)
    data0 = nc.variables[varName][:].squeeze()

    lons0 = lons0 - 360
    nc.close()

    if clevs is None:
        val1 = np.max([abs(np.min(data0)), abs(np.max(data0))])
        if val1<1.0:
            valExt=mf2(val1)
            pasul=mf2(valExt/12)
            lev1=(((np.arange(pasul/2.0,25*pasul/2.0,pasul))*(-1))[::-1])
            lev2=np.arange(pasul/2.0,25*pasul/2.0,pasul)
            clevs=np.append(lev1,lev2)
        elif val1<12.0:
            valExt=mf1(val1)
            pasul=mf1(valExt/12)
            lev1=(((np.arange(pasul/2.0,25*pasul/2.0,pasul))*(-1))[::-1])
            lev2=np.arange(pasul/2.0,25*pasul/2.0,pasul)
            clevs=np.append(lev1,lev2)
        else:
            valExt=np.int(val1)
            pasul=valExt/12
            lev1=(((np.arange(pasul/2.0,25*pasul/2.0,pasul))*(-1))[::-1])
            lev2=np.arange(pasul/2.0,25*pasul/2.0,pasul)
            clevs=np.append(lev1,lev2)
    norm = mpl.colors.BoundaryNorm(clevs, len(clevs) - 1)
    if txtLabel is None:
        txtLabel=' '
    f = plt.figure(figsize=(10,10))

    width = 7400000;
    height = 6800000;
    m = Basemap(width=width, height=height, resolution='l', projection='laea', lat_ts=65, lat_0=75, lon_0=-105.)
    m.drawcountries(linewidth=0.5)
    m.drawcoastlines(linewidth=0.5)

    x,y = m(lons0, lats0)
    im=m.pcolormesh(x,y,data0,cmap=colors, latlon=False,norm=norm)
    plt.title(tCentral, size=16)
    c = plt.colorbar(im, fraction=0.046, pad=0.04, orientation='vertical', extend='both',extendfrac='auto')
    c.set_label(txtLabel, size=14)
    c.set_ticks(clevs)
    font_size = 12 # Adjust as appropriate.
    c.ax.set_xticklabels(clevs)
    c.ax.tick_params(labelsize=font_size)
    f.savefig(output+imgout, dpi=400)
    plt.close()

