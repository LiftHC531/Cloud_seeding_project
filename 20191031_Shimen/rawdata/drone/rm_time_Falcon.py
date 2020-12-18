from time import time as cpu_time
import os, glob
import pandas as pd
import numpy as np

start_time = cpu_time()
undef = 20191031000000. 

def get_Falcon_file():
    ''' Similar with "ls -tr Falcon*.csv" '''
    Path = r''
    ff = sorted(glob.glob(Path+"*Falcon*.csv"), key=os.path.getmtime)
    #print(ff)
    return ff

def read_Falcon_data(ff):
    ''' Time (UTC) '''
    print("\033[44mReading file: {}\033[0m".format(ff))
    data = pd.read_csv(r''+ff,sep=',',encoding='big5') #gb18030
    print(data.head(10))
    col_name = list(data) #data.columns.tolist()
    col_name = [col for col in col_name]
    #print(col_name)
    var = np.empty(shape=data.shape,dtype=np.float64)
    print(var.shape)
    print("\033[94mData source: CALab, NCU\n" + \
          "Airborne instrument: Aerobox\nTime (UTC)\n" + \
          " Variables:{}\033[0m".format(col_name[:]))
          #" Variables:{}\033[0m".format(col_name[0:6+1]))
    for i in range(data.shape[1]):
        var[:,i] = data[col_name[i]]
    #lat = data[col_name[9]].tolist()#; print(lat)
    #lon = data[col_name[10]].tolist()#; print(lon)
    #date_utc = data[col_name[12]].tolist()
    #time = [str(dd)[8:14] for dd in var[:,12]]
    time = [np.round(np.float(dd)) for dd in var[:,12]]
    #print(var[:,1])

    newcl = 'remove Time (UTC)[將時間重複的資料歸0]'

    time_old = time[:]
    for i,ti in enumerate(time):
        #if np.float(ti) == 0.:
        #   print(i)
        j = ti
        #print('{},{}xx'.format(i,ti))
        if j  == time[i-1]:
           time[i]= undef 
           for k in range(i+1,len(time)):
               if j == time[k]:
                  time[k] = undef
        if i > 0 and i < len(time)-2:
           if np.abs(var[i,7]-var[i-1,7]) > 200. \
             or np.abs(var[i,7]-var[i+1,7]) > 200.:
              time[i]= undef 
 
    for i,ti in enumerate(time):
        if ti == 0.: time[i]= undef
            
    ts = []
    for i in range(len(time)):
        print('{:014d}'.format(np.int(time[i])))
        ts.append('{:14d}'.format(np.int(time[i])))
    data[newcl] = ts
    file_name = r'RemovedTime_Falcon_2019-10-31_Shimen_data.csv'
    os.system('rm -i '+file_name)
    data.to_csv(file_name, \
          encoding='big5',sep=',',index=False)

    return var, time

#--------------------------------------------------------------------
Files = get_Falcon_file()
var, time = read_Falcon_data(Files[0])

end_time = cpu_time(); end_time = (end_time - start_time)/60.0
print(os.path.basename(__file__)+" has done!\nTime elapsed: {:.2f}".format(end_time), "mins.")
