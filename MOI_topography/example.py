import os
from time import time as cpu_time
from osgeo import gdal, osr
import numpy as np
from numba import jit, int32, float32, int64, float64, types
import Ngl
#https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/39215/
#https://www.osgeo.cn/python_gdal_utah_tutorial/ch05.html

start_time = cpu_time()

def getSRSPair(dataset):
    '''
    獲得給定資料的投影參考系和地理參考系
    :param dataset: GDAL地理資料
    :return: 投影參考系和地理參考系
    '''
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(dataset.GetProjection())
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs

def geo2lonlat(dataset, x, y):
    '''
    將投影座標轉為經緯度座標（具體的投影座標系由給定資料確定）
    :param dataset: GDAL地理資料
    :param x: 投影座標x
    :param y: 投影座標y
    :return: 投影座標(x, y)對應的經緯度座標(lon, lat)
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    coords = sorted(coords[:2], reverse = True)
    return coords

def pts_geo2lonlat(dataset, xs, ys):
    prosrs, geosrs = getSRSPair(dataset)
    ct1 = osr.CoordinateTransformation(prosrs, geosrs)
    (nj,ni) = xs.shape
    lon = np.empty(shape=(nj,ni), dtype=np.float64)
    lat = np.empty(shape=(nj,ni), dtype=np.float64)
    for i in range(ni):
        for j in range(nj): 
            coords = ct1.TransformPoint(xs[j,i], ys[j,i])
            coords = sorted(coords[:2], reverse = True)
            lon[j,i] = coords[0]
            lat[j,i] = coords[1]
    return lon, lat  

def lonlat2geo(dataset, lon, lat):
    '''
    將經緯度座標轉為投影座標（具體的投影座標系由給定資料確定）
    :param dataset: GDAL地理資料
    :param lon: 地理座標lon經度
    :param lat: 地理座標lat緯度
    :return: 經緯度座標(lon, lat)對應的投影座標
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lat, lon)
    return coords[:2]

def imagexy2geo(dataset, row, col):
    '''
    根據GDAL的六引數模型將影像圖上座標（行列號）轉為投影座標或地理座標（根據具體資料的座標系統轉換）
    :param dataset: GDAL地理資料
    :param row: 畫素的列 x
    :param col: 畫素的行 y
    :return: 行列號(row, col)對應的投影座標或地理座標(x, y)
    '''
    gt = dataset.GetGeoTransform()
    originX = gt[0] #top left x
    originY = gt[3] #top left y
    pixelWidth = gt[1]  # w-e pixel resolution
    pixelHeight = gt[5] # n-s pixel resolution
    px = originX + row*pixelWidth + col*gt[2]
    py = originY + col*pixelHeight + row*gt[4]
    return px, py

@jit(types.Tuple((float64[:,:], float64[:,:]))\
(float64[:], int64[:], int64[:]), nopython=True, nogil=True)
def nb_pts_imagexy2geo(gt,rows,cols):
    ox = gt[0] #top left x
    oy = gt[3] #top left y
    pw = gt[1] # w-e pixel resolution
    ph = gt[5] # n-s pixel resolution
    px = np.empty(shape=(len(cols),len(rows)), dtype=np.float64)
    py = np.empty(shape=(len(cols),len(rows)), dtype=np.float64)
    for i,row in enumerate(rows):
        for j,col in enumerate(cols):
            px[j,i] = ox + row*pw + col*gt[2] 
            py[j,i] = oy + col*ph + row*gt[4]
    return px, py 

def pts_imagexy2geo(dataset, rows, cols):
    gt = np.float64(dataset.GetGeoTransform())
    return nb_pts_imagexy2geo(gt,rows,cols)

def geo2imagexy(dataset, x, y):
    '''
    根據GDAL的六引數模型將給定的投影或地理座標轉為影像圖上座標（行列號）
    :param dataset: GDAL地理資料
    :param x: 投影或地理座標x
    :param y: 投影或地理座標y
    :return: 影座標或地理座標(x, y)對應的影像圖上行列號(row, col)
    '''
    trans = dataset.GetGeoTransform()
    a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
    b = np.array([x - trans[0], y - trans[3]])
    return np.round(np.linalg.solve(a, b))  # 使用numpy的linalg.solve進行二元一次方程的求解

#-------------------------------------------------------------------------
#output_file = 'Northen_Taiwan.bin'
output_file = 'Shimen.bin'
os.system('rm -i '+output_file)
newFile = open(output_file, "wb")
#-------------------------------------------------------------------------
ds = gdal.Open(r'./tif_data/dem_20m.tif') #dataset
proj = ds.GetProjection()
print('Projection:\n'+proj)
cols = ds.RasterXSize 
rows = ds.RasterYSize
print('Data size (y, x):\n({}, {})'.format(rows,cols))
bands = ds.RasterCount


if output_file == 'Northen_Taiwan.bin':
   # Northen Taiwan
   lat = [24.473411, 25.311103]
   lon = [120.640933, 122.006585]
else:
   # Shimen
   lat = [24.798101, 24.826865]
   lon = [121.23145, 121.276594]
   
 
geo_cds_s = lonlat2geo(ds, lon[0], lat[1])
geo_cds_e = lonlat2geo(ds, lon[1], lat[0])
print(geo_cds_s)
print(geo_cds_e)
print('xy'+'-'*20)
xy_cds_s = geo2imagexy(ds, geo_cds_s[0], geo_cds_s[1]) 
xy_cds_e = geo2imagexy(ds, geo_cds_e[0], geo_cds_e[1]) 
xy_cds_e[0] = min(cols-1, xy_cds_e[0]) 
xy_cds_e[1] = min(rows-1, xy_cds_e[1]) 
nx = np.int(xy_cds_e[0] - xy_cds_s[0] + 1)
ny = np.int(xy_cds_e[1] - xy_cds_s[1] + 1)
xs = np.int(xy_cds_s[0])
ys = np.int(xy_cds_s[1])
print(xy_cds_s)
print(xy_cds_e)
print('\033[93mZoomed data size (y, x):\n({}, {})\033[0m'.format(ny,nx))


band = ds.GetRasterBand(1)
#array = band.ReadAsArray(0, 0, cols, rows)
hgt = np.float64(band.ReadAsArray(xs, ys, nx, ny))
print(hgt.shape)

''' lon, lat '''
lon = np.empty(shape=(ny, nx),dtype=np.float64)
lat = np.empty(shape=(ny, nx),dtype=np.float64)
ii = np.arange(xs, xs + nx)
jj = np.arange(ys, ys + ny)
(dumx,dumy) = pts_imagexy2geo(ds, ii, jj)
print(dumx[:,:])
print('xxx')
lon, lat = pts_geo2lonlat(ds, dumx, dumy)
''' output binary '''
newFile.write(bytearray(lon))
newFile.write(bytearray(lat))
newFile.write(bytearray(hgt))

print('-'*80)
row = 50; col = 10 
x = 149310.0; y = 2801530.0 
lon = 119.99990824129516  
lat = 25.319386554286126
print('圖上座標(row, col) -> 投影座標(x, y)：')
coords = imagexy2geo(ds, row, col)
print('(%s, %s)->(%s, %s)' % (row, col, coords[0], coords[1]))

print('投影座標(x, y) -> 圖上座標(row, col)：')
coords = geo2imagexy(ds, x, y)
print('(%s, %s)->(%s, %s)' % (x, y, coords[0], coords[1]))

print('投影座標(x, y) -> 經緯度(lon, lat):')
coords = geo2lonlat(ds, x, y)
print('(%s, %s)->(%s, %s)' % (x, y, coords[0], coords[1]))

print('經緯度(lon, lat) -> 投影座標(x, y)：')
coords = lonlat2geo(ds, lon, lat)
print('(%s, %s)->(%s, %s)' % (lon, lat, coords[0], coords[1]))

''' Plot '''


end_time = cpu_time(); end_time = (end_time - start_time)/60.0
print(os.path.basename(__file__)+" has done!\nTime elapsed: {:.2f}".format(end_time), "mins.")
