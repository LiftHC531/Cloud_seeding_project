import sys
sys.path.append("../../WRF_plot_tools")
from package import wrf_tools, colorbar_tables #local function
from time import time as cpu_time
import os, glob
import pandas as pd
import datetime
#import copy
import numpy as np
import Ngl, Nio
#import netCDF4 as nc
#import xarray as xr

start_time = cpu_time()
undef = -999. #9.96920996839e+36
ny = 160
nx = 230
sd_obs_mark_log = True

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
    #var = np.empty(shape=data.shape,dtype=np.float64)
    print("\033[94mData source: CALab, NCU\n" + \
          "Airborne instrument: Aerobox\nTime (LST, GMT+8)\n" + \
          " Variables:{}\033[0m".format(col_name[:]))
          #" Variables:{}\033[0m".format(col_name[0:6+1]))
    lat = data[col_name[9]].tolist()#; print(lat)
    lon = data[col_name[10]].tolist()#; print(lon)
    date_lst = data[col_name[12]].tolist()
    time = [str(dd)[8:14] for dd in date_lst]
    return np.float64(lon), np.float64(lat), time

def read_topo_bin():
    ff = r'../MOI_topography/Shimen.bin'
    print("\033[44mReading file: {}\033[0m".format(ff))
    dt = np.dtype((np.float64,(ny,nx)))
    lon = np.zeros(shape=(ny,nx),dtype=np.float64)
    lat = np.zeros(shape=(ny,nx),dtype=np.float64)
    hgt = np.zeros(shape=(ny,nx),dtype=np.float64)
    with open(ff, "rb") as f:
         lon = np.fromfile(f,dt,1)[0]
         lat = np.fromfile(f,dt,1)[0]
         hgt = np.fromfile(f,dt,1)[0]
    return lon, lat, hgt

def wks_setting(res):
    image_name = "Falcon_track_20190603"
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
    #res.vpWidthF = 0.74; res.vpHeightF = 0.54
    return wks, res

def add_polymarker(wks,plot,xd,yd,\
        index=5,size=5.,thick=10.,color="red"):
    """https://www.ncl.ucar.edu/Document/Functions/Built-in/NhlNewMarker.shtml"""
    poly_res = Ngl.Resources()
    poly_res.gsMarkerIndex = index #4   # choose circle as polymarker
    poly_res.gsMarkerSizeF = size       # select size to avoid streaking
    poly_res.gsMarkerThicknessF = thick #30.0
    #poly_res.gsMarkerOpacityF = 0.3
    poly_res.gsMarkerColor = color #purple4 # choose color
    return Ngl.add_polymarker(wks, plot, xd, yd, poly_res)


#--------------------------------------------------------------------
Files = get_Falcon_file()
(lon, lat, time) = read_Falcon_data(Files[0])
''' Deal with NaN '''
for i in range(len(lon)-1):
    if np.isnan(lon[i]) and i > 0:
       jr = i+1; jl = i-1
       while np.isnan(lon[jr]):
             jr += 1
       while np.isnan(lon[jl]):
             jl -= 1
       lon[i] = 0.5*(lon[jl]+lon[jr])
    if np.isnan(lat[i]) and i > 0:
       jr = i+1; jl = i-1
       while np.isnan(lat[jr]):
             jr += 1
       while np.isnan(lat[jl]):
             jl -= 1
       lat[i] = 0.5*(lat[jl]+lat[jr])


''' Plot '''
(lon_m, lat_m, hgt_m) = read_topo_bin()
lon_m = np.ravel(lon_m[:,:])
lat_m = np.ravel(lat_m[:,:])
hgt_m = np.ravel(hgt_m[:,:])
print(hgt_m.shape)
print(lat_m.shape)

res = Ngl.Resources()
(wks, res) = wks_setting(res)
res.sfXArray             = lon_m
res.sfYArray             = lat_m
#res.caXMissingV = undef ;res.caYMissingV = res.caXMissingV
res.sfMissingValueV = undef

# Contour options
res.cnFillOn           = True          # turn on contour fill
res.cnMissingValFillColor = [0.194771, 0.210458, 0.610458]
res.cnLinesOn          = True         # turn off contour lines
res.cnLineLabelsOn     = False         # turn off line labels
#res.cnFillMode            = "RasterFill"
res.lbLabelFontHeightF = 0.015              # default is a bit large

#print(np.arange(125,3125,125))
#cnLevels = np.concatenate(([ 0., 10.,  50.,  100., 250., 500.], \
#                           np.arange(1000.,3250,250.)),axis=None)
cnLevels = np.concatenate(([ 0., 150., 200., 250., 300., 350. ], \
                           np.arange(400.,650.,25.)),axis=None)
res.cnLevelSelectionMode  = "ExplicitLevels"
res.cnLevels = cnLevels

# Set resources necessary to get map projection correct.
#res.gsnAddCyclic = False
res.mpLimitMode        = "LatLon"
res.mpMinLatF = lat_m.min()
res.mpMaxLatF = lat_m.max()
res.mpMinLonF = lon_m.min()
res.mpMaxLonF = lon_m.max() ;print(res.mpMaxLonF)
#res.trYReverse         = True
#res.tfDoNDCOverlay     = True

# Set other map resources
res.mpGridAndLimbOn = False
res.mpOutlineOn     = False
#res.mpDataBaseVersion     = "MediumRes"
res.tmXBLabelFont = 26; res.tmYLLabelFont = res.tmXBLabelFont
res.tmXBLabelFontHeightF = 0.007; res.tmYLLabelFontHeightF = res.tmXBLabelFontHeightF
res.tmXBMajorThicknessF  = 15.0 ; res.tmYLMajorThicknessF = res.tmXBMajorThicknessF
res.tmBorderThicknessF   = 15.0


# Set color bar
res.lbTitleOn  =  True
res.lbTitlePosition  = "Top"
res.lbTitleString = "~F25~m"
res.lbTitleFontHeightF = 0.01
res.lbTitleOffsetF = -0.05
res.lbLabelFontHeightF = 0.008; res.lbLabelFont  = 26
res.pmLabelBarHeightF  = 0.80#0.65
res.pmLabelBarWidthF   = 0.07
res.pmLabelBarOrthogonalPosF = -0.01 #+R -L
res.pmLabelBarParallelPosF = 0.6 #+U -D


plot = Ngl.contour_map(wks,hgt_m,res)

# Plot flight track
# seeding time: 1250-1257 LST (0450-0457 UTC)
lnres = Ngl.Resources()
lnres.gsLineColor = 'white'
lnres.gsLineThicknessF = 10
for i in range(len(lon)-1):
    #print (time[i][0:4])
    xd = [lon[i], lon[i+1]]
    yd = [lat[i], lat[i+1]]
    if np.int(time[i][0:4]) < 1240:
       lnres.gsLineColor = 'white'
       plt_track = Ngl.add_polyline(wks, plot, xd, yd, lnres)
    elif np.int(time[i][0:4]) >= 1240 and np.int(time[i][0:4]) <= 1249:
       lnres.gsLineColor = 'red'
       plt_track = Ngl.add_polyline(wks, plot, xd, yd, lnres)
    elif np.int(time[i][0:4]) > 1249 and np.int(time[i][0:4]) < 1258:
       lnres.gsLineColor = 'purple'
       plt_track = Ngl.add_polyline(wks, plot, xd, yd, lnres)
    else:
       lnres.gsLineColor = 'orange'
       plt_track = Ngl.add_polyline(wks, plot, xd, yd, lnres)
   
    #if i > 0 and \
    #  np.int(time[i][0:4]) == 1240 and np.int(time[i-1][0:4]) < 1240:
    #   plt_marker = add_polymarker(wks,plot,lon[i],lat[i], \
    #         color='red')

plt_marker = add_polymarker(wks,plot,lon[0],lat[0], \
      color='red', size=10. )



if res.mpOutlineOn == False:
   #shapefile plot
   path = "/home/WRF/shapefile/"
   shp_file0 = "Shimen/COUNTY_MOI_1080617.shp" #"TWN_adm2.shp"
   wrf_tools.add_shapefile_polylines(path+shp_file0,wks,plot)
   if True:
      dam_shp_file = "Shimen/290-RESVR_storage_RNG.shp" #Shimen dam
      dam_shp_lines = wrf_tools.add_shapefile_polylines(path+dam_shp_file, \
                                              wks,plot,color="blue", thick=5)
if sd_obs_mark_log:
   (pt_o, dum) = wrf_tools.Reservoir_loc()
   plt_marker1 = add_polymarker(wks,plot,pt_o[:,1],pt_o[:,0], \
      index=4,size=0.01) 
   del pt_o, dum


Ngl.draw(plot)
Ngl.frame(wks)

Ngl.end()                        


end_time = cpu_time(); end_time = (end_time - start_time)/60.0
print(os.path.basename(__file__)+" has done!\nTime elapsed: {:.2f}".format(end_time), "mins.")
