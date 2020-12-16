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
    ff = sorted(glob.glob(Path+"Falcon*.csv"), key=os.path.getmtime)
    #print(ff)
    return ff

def read_Falcon_data(ff):
    data = pd.read_csv(r''+ff,sep=',',encoding='big5') #gb18030
    print(data.head(10))
    col_name = list(data) #data.columns.tolist()
    col_name = [col for col in col_name]
    #print(col_name)
    var = np.empty(shape=data.shape,dtype=np.float64)
    print(var.shape)
    print("\033[94mData source: CALab, NCU\n" + \
          "Airborne instrument: Aerobox\nTime (LST, GMT+8)\n" + \
          " Variables:{}\033[0m".format(col_name[:]))
          #" Variables:{}\033[0m".format(col_name[0:6+1]))
    for i in range(data.shape[1]):
        var[:,i] = data[col_name[i]]
    #lat = data[col_name[9]].tolist()#; print(lat)
    #lon = data[col_name[10]].tolist()#; print(lon)
    #date_lst = data[col_name[12]].tolist()
    time = [str(dd)[8:14] for dd in var[:,12]]
    #print(var[:,1])
    return var, time

def rearange_data(var, time):
    'per second'
    nv = np.int(len(var[0,:]))
    #--- 12:30:00 - 12:59:59 LST ---
    t_labels = np.arange(123000,123059+1)
    for i in range(1,59-30+1):
        ii1 = 123000+100*i
        ii2 = 123059+100*i
        t_labels = np.concatenate((t_labels, np.arange(ii1,ii2+1)), axis=None)
    #print(t_labels)
    #--- 13:00:00 - 13:10:00 LST ---
    for i in range(10):
        ii1 = 130000+100*i
        ii2 = 130059+100*i
        t_labels = np.concatenate((t_labels, np.arange(ii1,ii2+1)), axis=None)
    t_labels = np.concatenate((t_labels, [131000]), axis=None)
    print(t_labels.shape)
    print(t_labels)
    nt = np.int(len(t_labels))
    v = np.empty(shape=(nt,nv), dtype=np.float64)
    v[:,:] = undef
    for t,t_label in enumerate(t_labels):
        for i,ti in enumerate(time):
            if np.float(ti) == np.float(t_label):
               v[t,:] = np.float64(var[i,:])
    return v, t_labels

def wks_setting(res):
    image_name = "timeseries_Falcon_20190603"
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
var, time = read_Falcon_data(Files[0])
vv, tt = rearange_data(var, time); del var, time
print(vv.shape)
nx, ny = np.int32(vv.shape)
xx = np.arange(len(tt)) #x-axis (Time)

# Time Labels for plot    
t_labels = [1230, 1235, 1240, 1245, 1250, 1255, 
            1300, 1305, 1310,
           ]
# LST -> UTC
t_labels_utc = [] 
xarray = []
for t_label in t_labels:
    utc = "{:04d}".format(np.int(t_label)-800)
    t_labels_utc.append(utc)   
    for i,ti in enumerate(tt):
        if np.float(ti) == t_label*100.: 
           xarray.append(i)
# Find the time index after fire
for i,ti in enumerate(tt):
    if np.float(ti) == 125700:
       fire_i = i
print(xarray)
''' Plot '''
i = 7
res = Ngl.Resources()
(wks, res) = wks_setting(res)
#res.trYMinF  = 25.0   # Limits for Y axis.  The limits
#res.trYMaxF  = 30.0
res.xyLineColor = "black"
res.caXMissingV = undef;res.caYMissingV = res.caXMissingV
res.xyLineThicknesses = 20
res2 = copy.deepcopy(res)
res2.xyLineColor = "blue"
res2.trYMinF  = 0.0   # Limits for Y axis.  The limits
res2.trYMaxF  = 5.0
#res.tmYUseLeft = False
#res.tmYRMode = "Explicit"
#res.tmYRLabelsOn = True
res.tmYRLabelFontColor = "blue"
unit = ['hPa', '~S~o~N~C', 'K', '%', 
        'g kg~S~-1~N~', '~S~o~N~C', 
        'g m~S~-3~N~', 'A.M.S.L.(m)']
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

res_d = copy.deepcopy(res)
res_d.xyLineColor = "red"
res_d.xyDashPattern = 2
fire = np.arange(1000.)
xf = np.empty(shape=len(fire),dtype=np.float64)
xf[:] = fire_i 

plot = []

plot.append(Ngl.xy(wks, xx, vv[:,i],res))
plot.append(Ngl.xy(wks, xf, fire,res_d))
#plot.append(Ngl.xy(wks, xx, vv[:,4],res2))
Ngl.overlay(plot[0],plot[1])

Ngl.draw(plot[0])
#Ngl.draw(plot[1])
Ngl.frame(wks)

Ngl.end()

end_time = cpu_time(); end_time = (end_time - start_time)/60.0
print(os.path.basename(__file__)+" has done!\nTime elapsed: {:.2f}".format(end_time), "mins.")

