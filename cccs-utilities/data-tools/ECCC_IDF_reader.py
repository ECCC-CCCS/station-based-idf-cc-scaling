"""Read IDF data from ECCC IDF .txt files

Notes:
-Should work with v3.20 IDF files.  Not guaranteed with other IDF file versions!

Inputs: 
-IDF file name (including full path to file)

Outputs:
-a dictionary object that contains a collection of other dictionaries:
  -a dictionary with location/ID information (['location'])
  -a dictionary with timespan information (['period'])
  -a dictionary with IDF rate data, in a Pandas DataFrame (['IDF_rates'])
  -a dictionary with IDF rate statistical confidence data, in a Pandas DataFrame (['IDF_confidence'])
"""

def read_ECCC_IDF(filename):      

        import pandas as pd
        import numpy as np
        from os import path
        import re
  
        idfDict={}
        idfDict["location"]={}
        basename=path.basename(filename)
        idfDict["location"]["ID"]=basename.split("_")[7]
        start=idfDict["location"]["ID"]+'_'
        end='.txt'
        name = re.search('%s(.*)%s' % (start, end), basename).group(1)
        idfDict["location"]["name"]=name
        
        with open(filename, "r", encoding = "ISO-8859-1") as f:
            while True:
                line = f.readline()
                if "Latitude" in line: #Get lat/lon values
                    tokens=line.split()
                    idfDict["location"]["latitude"]=float(tokens[1]) + float(tokens[2].split("'")[0]) / 60. #extract degrees, fractional degrees from line; convert to decimal (float)
                    idfDict["location"]["longitude"]=float(tokens[4]) + float(tokens[5].split("'")[0]) / 60. #extract degrees, fractional degrees from line; convert to decimal (float). 
                if "Years/Années" in line:  #Get input precip data range
                    tokens=line.split()
                    idfDict["period"]={}
                    idfDict["period"]["start_date"]=int(tokens[2])
                    idfDict["period"]["end_date"]=int(tokens[4])
                    idfDict["period"]["total_years"]=int(tokens[8])
                if "Return Period Rainfall Rates" in line:  #Get actual data lines
                    data = [f.readline() for i in range(24)]#load 23 lines following occurrence of string into 'data'
                    break #jump to next code, once data extracted

        returnPeriods = [str(i)+' year' for i in data[4].rstrip().split()[1:7]] #extract return periods (years)
        IDF_data = [data[i] for i in [6,8,10,12,14,16,18,20,22]] #trim to just get lines with idf values.
        IDF_confidence_data=[data[i] for i in [7,9,11,13,15,17,19,21,23]] #trim to just get lines with confidence values.
        nReturnPeriods=len(returnPeriods)
        nDurations=len(IDF_data)
        idf=np.empty([nDurations,nReturnPeriods])
        idf_confidence=np.empty([nDurations,nReturnPeriods])
        rates=[]
        for i,line in enumerate(IDF_data):
            rates.append(line.rstrip().split()[0]+' '+line.rstrip().split()[1])
            idf[i,:]=[float(i) for i in line.rstrip().split()[2:-1]] #extract idf values from lines, convert to float, add to idfHist array
        idf_df=pd.DataFrame(idf,index=rates,columns=returnPeriods)
        idfDict["IDF_rates"]=idf_df
        for i,line in enumerate(IDF_confidence_data):
            line=line.rstrip()
            line=line.replace("+/-","")
            line=line.split()[0:6]
            idf_confidence[i,:]=[float(i) for i in line]
        idf_confidence_df=pd.DataFrame(idf_confidence,index=rates,columns=returnPeriods)
        idfDict["IDF_rate_confidence"]=idf_confidence_df
        return idfDict
        
def main():
    #Dummy calls - can modify for real use if required
    return read_ECCC_IDF("IDF_file.txt")

if __name__ == "__main__":
    main()

