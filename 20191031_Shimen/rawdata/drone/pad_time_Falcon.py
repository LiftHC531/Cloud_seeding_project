from time import time as cpu_time
import os, glob
import pandas as pd
import numpy as np

start_time = cpu_time()

def get_Falcon_file():
    ''' Similar with "ls -tr Falcon*.csv" '''
    Path = r''
    ff = sorted(glob.glob(Path+"*Falcon*.csv"), key=os.path.getmtime)
    #print(ff)
    return ff

def read_Falcon_data(ff):
    ''' Time (UTC) '''
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
    time = [str(dd)[8:14] for dd in var[:,12]]
    #print(var[:,1])

    newcl = 'Padding Time (UTC)[以1秒填補]'
    for i,ti in enumerate(time):
        if np.float(ti) == 0.:
           time[i] = np.float(time[i-1])

    #for i,ti in enumerate(time[0:340]):
    for i,ti in enumerate(time):
        #if np.float(ti) == 0.:
        #   print(i)
        j = np.float(ti)
        #print('{},{}xx'.format(i,ti))
        if j  == np.float(time[i-1]):
           time[i]= np.float(time[i-1]) + 1.
           s60 = np.int('{:06d}'.format(np.int(time[i]))[4:])
           m60 = np.int('{:06d}'.format(np.int(time[i]))[2:4])
           if s60 >= 60: time[i] = time[i] - 60. + 100.
           if m60 >= 60: time[i] = time[i] - 6000. + 10000.
           #print('{},{}'.format(i,ti))
           for k in range(i+1,len(time)):
               if j == np.float(time[k]):
                  time[k] = np.float(time[k-1]) + 1.
                  s60 = np.int('{:06d}'.format(np.int(time[k]))[4:])
                  m60 = np.int('{:06d}'.format(np.int(time[k]))[2:4])
                  if s60 >= 60: time[k] = time[k] - 60. + 100.
                  if m60 >= 60: time[k] = time[k] - 6000. + 10000.
    ts = []
    for i in range(len(time)):
        ts.append('20191031{:06d}'.format(np.int(time[i])))
    data[newcl] = ts
    data.to_csv(r'PaddedTime_Falcon_2019-10-31_Shimen_data.csv', \
          encoding='big5',sep=',',index=False)

    return var, time

#--------------------------------------------------------------------
Files = get_Falcon_file()
var, time = read_Falcon_data(Files[0])

end_time = cpu_time(); end_time = (end_time - start_time)/60.0
print(os.path.basename(__file__)+" has done!\nTime elapsed: {:.2f}".format(end_time), "mins.")
