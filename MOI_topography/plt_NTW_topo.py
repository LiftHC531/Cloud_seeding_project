import sys
sys.path.append("/home/mlhchen/GIT/WRF_plot_tools")
from package import wrf_tools, colorbar_tables #local function
from time import time as cpu_time
import os
import copy
import numpy as np
import pandas as pd
import Ngl


start_time = cpu_time()
undef = -999.#9.96920996839e+36
ny = 4624 
nx = 6898
smooth_log = True 
rain_gauge_mark_log = 1
radar_mark_log = 1
precip_mark_log = 0 
precip2_mark_log = 0 

def read_bin():
    ff = r'Northen_Taiwan.bin'
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

def read_rain_guage_loc():
    ff = r'../2020_TW_rain_gauge_loc.csv'
    print("\033[44mReading file: {}\033[0m".format(ff))
    data = pd.read_csv(ff,sep=',',encoding='big5') #gb18030
    #print(data.head(10))
    col_name = list(data) #data.columns.tolist()
    col_name = [col.strip() for col in col_name]
    #print(col_name)
    print("\033[94mData source: CWB, Taiwan\n" + \
          "Information of Rain guage\n" + \
          " {}\033[0m".format(col_name[:]))
    st_id = data[col_name[0]].tolist()#; print(st_id)
    hgt = data[col_name[2]].tolist()#; print(hgt)
    lon = data[col_name[3]].tolist()#; print(lon)
    lat = data[col_name[4]].tolist()#; print(lat)
    #date = data[col_name[7]].tolist()#; print(date)

    return lon, lat

def read_weather_radar_loc():
    ff = r'../2020_TW_weather_radar_loc.csv'
    data = pd.read_csv(ff,sep=',',encoding='big5') #gb18030
    #print(data.head(10))
    col_name = list(data) #data.columns.tolist()
    col_name = [col.strip() for col in col_name]
    #print(col_name)
    print("\033[94mData source: Taiwan\n" + \
          "Information of Weather Radar\n" + \
          " {}\033[0m".format(col_name[:]))
    st_id = data[col_name[5]].tolist(); print(st_id)
    lon = data[col_name[2]].tolist()#; print(lon)
    lat = data[col_name[3]].tolist()#; print(lat)
    hgt = data[col_name[4]].tolist()#; print(hgt)
    return lon, lat


def read_precip_loc():
    ff = r'../precip_loc.csv'
    data = pd.read_csv(ff,sep=',',encoding='big5') #gb18030
    #print(data.head(10))
    col_name = list(data) #data.columns.tolist()
    col_name = [col.strip() for col in col_name]
    #print(col_name)
    print("\033[94mData source: Taiwan\n" + \
          "Information of obs.\n" + \
          " {}\033[0m".format(col_name[:]))
    st_id = data[col_name[0]].tolist()#; print(st_id)
    lon = data[col_name[2]].tolist()#; print(lon)
    lat = data[col_name[1]].tolist()#; print(lat)
    hgt = data[col_name[3]].tolist()#; print(hgt)
    #date = data[col_name[7]].tolist()#; print(date)
    return lon, lat

def read_precip2_loc():
    ff = r'../precip2_loc.csv'
    data = pd.read_csv(ff,sep=',',encoding='big5') #gb18030
    #print(data.head(10))
    col_name = list(data) #data.columns.tolist()
    col_name = [col.strip() for col in col_name]
    #print(col_name)
    print("\033[94mData source: Taiwan\n" + \
          "Information of obs.\n" + \
          " {}\033[0m".format(col_name[:]))
    st_id = data[col_name[0]].tolist()#; print(st_id)
    lon = data[col_name[2]].tolist()#; print(lon)
    lat = data[col_name[1]].tolist()#; print(lat)
    hgt = data[col_name[3]].tolist()#; print(hgt)
    #date = data[col_name[7]].tolist()#; print(date)
    return lon, lat

def wks_setting(res):
    image_name = "Northen_TW_topography"
    wks_type = "png"
    print("\033[44m---Plot: {}.{} ---\033[0m".format(image_name,wks_type))
    rlist = Ngl.Resources()
    rlist.wkWidth  = 3000 #page resolution
    rlist.wkHeight = 3000
    wks = Ngl.open_wks(wks_type,image_name,rlist)
    '''
    cmap = Ngl.read_colormap_file("MPL_terrain")
    cmap1 = []
    for cp in cmap:
        print(cp)
        print('---')
        #print(str(cp).replace('[','').replace(']','').replace('  ',' ').strip().split(' '))
        dum = str(cp).replace('[','').replace(']','').strip()
        dum = dum.replace('       ',' ').replace('   ',' ').replace('  ',' ')
        dum = dum.replace(' ',',').split(',')[0:3]
        print(dum)
        cmap1.append(dum)
    cmap1 = [[1,1,1],[0,0,0]]+[cmap1[0]]+ cmap1[30:len(cmap1)]
    print(cmap1)
    cmap1 = np.float32(cmap1)
    print(cmap1)
    #cmap1 = np.concatenate(([cmap[0]], cmap[30:]), axis=0)
    #print(len(cmap1))
    #print(cmap1)
    #Ngl.define_colormap(wks, cmap1 )
    '''
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
(lon, lat, hgt) = read_bin()
if smooth_log: 
   sth = 10
   lon1d = np.ravel(lon[::sth,::sth])
   lat1d = np.ravel(lat[::sth,::sth])
   hgt1d = np.ravel(hgt[::sth,::sth])
else:
   lon1d = np.ravel(lon[:,:])
   lat1d = np.ravel(lat[:,:])
   hgt1d = np.ravel(hgt[:,:])
print(hgt1d.shape)
print(lat1d.shape)
hgt1d = np.where(hgt1d < 1.e-14, undef, hgt1d)
hgt1d = np.where((hgt1d == undef) & (lon1d < 121.82) & (lon1d > 121.39) \
                 & (lat1d < 25.145) , 0., hgt1d)
hgt1d = np.where((hgt1d == undef) & (lon1d >= 121.39) & (lon1d < 121.83) \
                 & (lat1d < 24.73) , 0., hgt1d)

print(lat1d[10])
print(np.min(hgt1d[:]))

''' plot '''
res = Ngl.Resources()
(wks, res) = wks_setting(res)
res.sfXArray             = lon1d   
res.sfYArray             = lat1d
#res.caXMissingV = undef ;res.caYMissingV = res.caXMissingV
res.sfMissingValueV = undef

# Contour options
res.cnFillOn           = True          # turn on contour fill
res.cnMissingValFillColor = [0.194771, 0.210458, 0.610458] 
res.cnLinesOn          = False         # turn off contour lines
res.cnLineLabelsOn     = False         # turn off line labels
res.cnFillMode            = "RasterFill"
res.lbLabelFontHeightF = 0.015              # default is a bit large

#print(np.arange(125,3125,125))
cnLevels = np.concatenate(([ 0., 10.,  50.,  100., 250., 500.], \
                           np.arange(1000.,3250,250.)),axis=None)
res.cnLevelSelectionMode  = "ExplicitLevels"
res.cnLevels = cnLevels

# Set resources necessary to get map projection correct.
#res.gsnAddCyclic = False
res.mpLimitMode        = "LatLon"
res.mpMinLatF = lat1d.min()
res.mpMaxLatF = lat1d.max() 
res.mpMinLonF = lon1d.min()
res.mpMaxLonF = lon1d.max() ;print(res.mpMaxLonF)
#res.trYReverse         = True
#res.tfDoNDCOverlay     = True

# Set other map resources
res.mpGridAndLimbOn = False
res.mpOutlineOn     = False
#res.mpDataBaseVersion     = "MediumRes"
res.tmXBLabelFont = 26; res.tmYLLabelFont = res.tmXBLabelFont
res.tmXBLabelFontHeightF = 0.010; res.tmYLLabelFontHeightF = res.tmXBLabelFontHeightF
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


plot = Ngl.contour_map(wks,hgt1d,res)

if res.mpOutlineOn == False:
   #shapefile plot
   path = "/home/WRF/shapefile/"
   shp_file0 = "Shimen/COUNTY_MOI_1080617.shp" #"TWN_adm2.shp"
   wrf_tools.add_shapefile_polylines(path+shp_file0,wks,plot,thick=7)
   if False:
      dam_shp_file = "Shimen/290-RESVR_storage_RNG.shp" #Shimen dam
      dam_shp_lines = wrf_tools.add_shapefile_polylines(path+dam_shp_file, \
                                              wks,plot,color="blue")
if rain_gauge_mark_log:
   (ptx,pty) = read_rain_guage_loc()
   plt_marker = add_polymarker(wks,plot,ptx[:],pty[:], \
      index=1,size=0.03)
   del ptx, pty

if radar_mark_log:
   (ptx,pty) = read_weather_radar_loc() 
   plt_marker2 = add_polymarker(wks,plot,ptx[:],pty[:], \
      index=7,size=0.015, color="white")
   del ptx, pty

if precip_mark_log:
   (ptx,pty) = read_precip_loc()
   plt_marker3 = add_polymarker(wks,plot,ptx[:],pty[:], \
      index=1,size=0.03)
      #index=4,size=0.005)
   del ptx, pty

if precip2_mark_log:
   (ptx,pty) = read_precip2_loc()
   plt_marker3 = add_polymarker(wks,plot,ptx[:],pty[:], \
      index=1,size=0.03, color="blue")
      #index=4,size=0.005)
   del ptx, pty

Ngl.draw(plot)
Ngl.frame(wks)

Ngl.end()




end_time = cpu_time(); end_time = (end_time - start_time)/60.0
print(os.path.basename(__file__)+" has done!\nTime elapsed: {:.2f}".format(end_time), "mins.")
