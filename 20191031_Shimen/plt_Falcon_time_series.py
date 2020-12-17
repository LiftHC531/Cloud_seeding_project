import sys
sys.path.append("../../WRF_plot_tools")
from package import wrf_tools, colorbar_tables #local function
from time import time as cpu_time
import os, glob
import pandas as pd
import datetime
import copy
import numpy as np
import Ngl, Nio
#import netCDF4 as nc
#import xarray as xr

start_time = cpu_time()
undef = np.float64(-999.) #9.96920996839e+36
UTC_log = 1 # 0: LST, 1: UTC

def get_Falcon_file():
    ''' Similar with "ls -tr Falcon*.csv" '''
    Path = './rawdata/drone/'
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
    time = [str(dd)[8:14] for dd in var[:,13]]
    #print(var[:,1])

    return var, time

def rearange_data(var, time):
    'per second'
    nv = np.int(len(var[0,:]))
    #--- 05:00:00 - 05:59:59 UTC ---
    ti = 50000
    tf = 50059
    t_labels = np.arange(ti, tf+1)
    for i in range(1,59+1):
        ii1 = ti+100*i
        ii2 = tf+100*i
        t_labels = np.concatenate((t_labels, np.arange(ii1,ii2+1)), axis=None)
    #print(t_labels)
    #--- 06:00:00 - 06:05:00 UTC ---
    ti = 60000
    tf = 60059
    for i in range(5):
        ii1 = ti+100*i
        ii2 = tf+100*i
        t_labels = np.concatenate((t_labels, np.arange(ii1,ii2+1)), axis=None)
    t_labels = np.concatenate((t_labels, [50500]), axis=None)
    print(t_labels.shape)
    print(t_labels)
    nt = np.int(len(t_labels))
    v = np.empty(shape=(nt,nv), dtype=np.float64)
    v[:,:] = undef

    for t,t_label in enumerate(t_labels):
        for i,ti in enumerate(time):
            if np.float(ti) == np.float(t_label):
               v[t,:] = np.float64(var[i,:])
    #Check NaN
    v = np.where(np.isnan(v), undef, v)    
    v[:,7] = np.where(v[:,7] > 1200., undef, v[:,7])    
    return v, t_labels

def wks_setting(res,vn):
    image_name = "{}_timeseries_Falcon_20191031".format(vn)
    wks_type = "png"
    print("\033[44m---Plot: {}.{} ---\033[0m".format(image_name,wks_type))
    rlist = Ngl.Resources()
    rlist.wkWidth  = 3000 #page resolution
    rlist.wkHeight = 3000
    wks = Ngl.open_wks(wks_type,image_name,rlist)
    Ngl.define_colormap(wks, colorbar_tables.TW_terrain())
    #Ngl.define_colormap(wks, "MPL_terrain")
    res.nglMaximize = True
    res.nglDraw  = False; res.nglFrame = False
    res.vpWidthF = 0.9; res.vpHeightF = 0.3
    return wks, res


#--------------------------------------------------------------------
Files = get_Falcon_file()
var, time = read_Falcon_data(Files[1])
#print(time)
vv, tt = rearange_data(var, time); del var, time
print(vv.shape)
nx, ny = np.int32(vv.shape)
xx = np.arange(len(tt)) #x-axis (Time)

# Time Labels for plot    
t_labels_utc = np.concatenate((np.arange(500,560,5), [600,605]),axis=None)
t_labels_utc = t_labels_utc.tolist() # integer -> string
# UTC -> LST
t_labels = [] 
xarray = []
for t,t_label in enumerate(t_labels_utc):
    t_labels_utc[t] = "{:04d}".format(np.int(t_label))
    lst = "{:04d}".format(np.int(t_label+800))
    t_labels.append(lst)   
    for i,ti in enumerate(tt):
        if np.float(ti) == t_label*100.: 
           xarray.append(i)
# Find the time index after seeding 
for i,ti in enumerate(tt):
    if np.float(ti) == 52800:
       fire_i = i
print(xarray)
#print(t_labels_utc)
''' Plot '''
var_name = ['P','T','th','RH','qv','Td','PM25','hgt']
for i in range(0,7+1):
    res = Ngl.Resources()
    (wks, res) = wks_setting(res,var_name[i])
    #res.trYMinF  = 25.0   # Limits for Y axis.  The limits
    #res.trYMaxF  = 30.0
    res.xyLineColor = "black"
    res.caXMissingV = undef;res.caYMissingV = res.caXMissingV
    res.xyLineThicknesses = 20
    res.tmYRLabelFontColor = "blue"
    #http://www.ncl.ucar.edu/Document/Graphics/Images/font33.png
    unit = ['P (hPa)', 'T (~S~o~N~C)', '~F33~q~F25~ (K)', 'RH (%)', 
        'q~B~v~N~ (g kg~S~-1~N~)', 'T~B~d~N~ (~S~o~N~C)', 
        'PM~B~2.5~N~ (~F33~m~F25~g m~S~-3~N~)',
        'A.M.S.L. (m)']
    res.tiYAxisString = "~F25~"+unit[i]
    res.trXMinF = 0    # Limits for X axis.  The limits
    res.trXMaxF = nx-1
    res.tmXBMode   = "Explicit"
    res.tmXBValues = xarray
    if UTC_log: t_labels = t_labels_utc 
    res.tmXBLabels = t_labels 
    res.tmXBMinorValues = np.arange(0,nx+1,60)

    t_format = ['LST','UTC']
    res.tiXAxisString = "~F25~Time ({})".format(t_format[UTC_log])
    res.tmBorderThicknessF = 10.0
    res.tmXBMajorThicknessF = res.tmBorderThicknessF; res.tmYLMajorThicknessF = res.tmBorderThicknessF 
    res.tmXBMinorThicknessF = 10.0
    res.tmYLMinorThicknessF = 10.0
    res.tmYRMinorThicknessF = 10.0
    res.tmYRMajorThicknessF = res.tmYLMajorThicknessF 
    res.tmXBLabelFont = 26; res.tmYLLabelFont = res.tmXBLabelFont
    res.tmYRLabelFont = res.tmYLLabelFont
    res.tmXBLabelFontHeightF = 0.015; res.tmYLLabelFontHeightF = res.tmXBLabelFontHeightF
    res.tmYRLabelFontHeightF = res.tmYLLabelFontHeightF
    
    if ~('res_d' in locals()):
       res_d = copy.deepcopy(res)
       res_d.xyLineColor = "red"
       res_d.xyDashPattern = 2
       fire = np.arange(1000.)
       xf = np.empty(shape=len(fire),dtype=np.float64)
       xf[:] = fire_i 

    plot = []

    plot.append(Ngl.xy(wks, xx, vv[:,i], res))
    plot.append(Ngl.xy(wks, xf, fire, res_d))
    Ngl.overlay(plot[0],plot[1])

    Ngl.draw(plot[0])
    Ngl.frame(wks)
    del res

Ngl.end()

end_time = cpu_time(); end_time = (end_time - start_time)/60.0
print(os.path.basename(__file__)+" has done!\nTime elapsed: {:.2f}".format(end_time), "mins.")

