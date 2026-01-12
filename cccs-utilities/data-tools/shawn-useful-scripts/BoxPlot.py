import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import pylab
from pylab import plot, show, savefig, xlim, figure, ylim, legend, boxplot, setp, axes
import matplotlib.patches as mpatches


def setBoxColors(bp):
    setp(bp['boxes'][0], color='#377eb8',facecolor='blue', alpha=0.3)
    setp(bp['caps'][0], color='#377eb8',linewidth=2, alpha=0.3)
    setp(bp['caps'][1], color='#377eb8',linewidth=2, alpha=0.3)
    setp(bp['whiskers'][0], color='#377eb8',linestyle='-', linewidth=2, alpha=0.3)
    setp(bp['whiskers'][1], color='#377eb8',linestyle='-', linewidth=2, alpha=0.3)
    #setp(bp['fliers'][0],  marker='*',markersize=8, markeredgecolor='blue', markerfacecolor='blue')
    setp(bp['medians'][0], color='#377eb8',linewidth=5)

    setp(bp['boxes'][1], color='#dede00',facecolor='#dede00', alpha=0.3)
    setp(bp['caps'][2], color='#dede00',linewidth=2, alpha=0.3)
    setp(bp['caps'][3], color='#dede00',linewidth=2, alpha=0.3)
    setp(bp['whiskers'][2], color='#dede00',linestyle='-', linewidth=2, alpha=0.3)
    setp(bp['whiskers'][3], color='#dede00',linestyle='-', linewidth=2, alpha=0.3)
    #setp(bp['fliers'][1], marker='*',markersize=8, markeredgecolor='orange', markerfacecolor='orange')
    setp(bp['medians'][1], color='#dede00',linewidth=5)
    
    setp(bp['boxes'][2], color='#a65628',facecolor='red', alpha=0.3)
    setp(bp['caps'][4], color='#a65628',linewidth=2, alpha=0.3)
    setp(bp['caps'][5], color='#a65628',linewidth=2, alpha=0.3)
    setp(bp['whiskers'][4], color='#a65628',linestyle='-', linewidth=2, alpha=0.3)
    setp(bp['whiskers'][5], color='#a65628',linestyle='-', linewidth=2, alpha=0.3)
    #setp(bp['fliers'][2], marker='*',markersize=8, markeredgecolor='red', markerfacecolor='red')
    setp(bp['medians'][2], color='#a65628',linewidth=5)    


##############################################################
#Put here the name of the variable
varName='cold days'
# Put here the name of the variable with the units (this will appear on the OY ax)
#oyLabel=r'$\Delta$'+" Wmaxmax [m/s]"
oyLabel='Annual Number of Cold Days (<-20\xb0C)'

#Put here the two future periods
periode1='2021-2050'
periode2='2051-2080'

#############################
#Put here the folder for the input and output
input='G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/05 - Personal/DeGroot/Decision Making Exercise/Input Data/Input Boxplot/'
output= 'G:/30. CLIMATE SERVICES DATA PRODUCTS OFFICE/05 - Personal/DeGroot/Decision Making Exercise/Output Data/Boxplots/CD/'

data0 = pd.read_csv(input+'CD_boxplot_data.csv', sep=',')

#put here the name of the CSV foile containing the deltas for each period and each RCP
df_newT=data0.iloc[:,1:]
df_newT.index=data0.iloc[:,0]
mask = ~np.isnan(df_newT[' rcp26_2050']) & ~np.isnan(df_newT[' rcp26_2085'])

###############################
dataH50 =[np.array(df_newT[' rcp26_2050'][mask],dtype=float),np.array(df_newT[' rcp45_2050'],dtype=float),np.array(df_newT[' rcp85_2050'],dtype=float)]
dataH85 =[np.array(df_newT[' rcp26_2085'][mask],dtype=float),np.array(df_newT[' rcp45_2085'],dtype=float),np.array(df_newT[' rcp85_2085'],dtype=float)]

fig = figure(figsize=(16,32))
ax = axes()

boxX=boxplot(dataH50,whis=[10,90], positions = [1.1, 1.5, 1.9], patch_artist=True,widths = 0.3, showfliers=False)
setBoxColors(boxX)
boxX=boxplot(dataH85,whis=[10,90],positions = [3.1, 3.5,3.9], patch_artist=True,widths = 0.3, showfliers=False)
setBoxColors(boxX)

ax.set_xticks([1.5, 3.5])
ax.set_xticklabels([periode1, periode2],fontsize=12)
ticklabels = ax.get_yticklabels()

xlim(0,5)

orange_patch = mpatches.Patch(color='#377eb8', label='RCP 2.6 (Low Emission Scenario)')
blue_patch = mpatches.Patch(color='#dede00', label='RCP 4.5 (Moderate Emission Scenario)')
red_patch = mpatches.Patch(color='#a65628', label='RCP 8.5 (High Emission Scenario)')
plt.axhline(y=0.0, linewidth=1.5, color = 'k')
plt.legend(handles=[orange_patch, blue_patch, red_patch],fontsize=32,loc=2, bbox_to_anchor=(0.01,1))
#plt.axvspan(0.5, 2.5, ymin=0, ymax=100, color='lightgrey',alpha=0.5, label='2021-2050')
#plt.axvspan(2.5, 4.5, ymin=0, ymax=100, color='grey',alpha=0.7, label='2051-2080')
plt.xticks(fontsize=60)
plt.yticks(np.arange(0, 5, step=1), fontsize=60)
plt.ylabel(oyLabel, fontsize=72)
#plt.yticks(np.arange(0, 100, step=5))
plt.grid(b=None, which='both', axis='y')
#plt.ylim(0, 150)

rect_2050=mpatches.Rectangle((0.5,0), 2, 2, color='k', fill=None, alpha=1, linewidth=5)
rect_2080=mpatches.Rectangle((2.5,0), 2, 1, color='k', fill=None, alpha=1, linewidth=5)
plt.gca().add_patch(rect_2050)
plt.gca().add_patch(rect_2080)
plt.text(1,2.05,'2021-2050',fontsize=35)
plt.text(3,1.05,'2051-2080',fontsize=35)

plt.ylim(0, 5)

#Put here the name of the file you want to save as figure
plt.savefig(output+varName+'_boxplot_whis1090.png',bbox_inches='tight', pad_inches=0.3, dpi=400)
