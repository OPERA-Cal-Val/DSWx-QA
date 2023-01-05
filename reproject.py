import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import geopandas as gpd
from shapely.geometry import box
from rasterio.crs import CRS
from rasterio.warp import transform_bounds
from rasterio.warp import calculate_default_transform, reproject, Resampling
import rioxarray
import xarray
from rioxarray.merge import merge_arrays
import os
from osgeo import gdal


bucket_name = 'opera-pst-rs-pop1'
local_path = "C:/Users/Matthew Bonnema/Documents/dswx_data/wtr/"
local_reproj = "C:/Users/Matthew Bonnema/Documents/dswx_data/wrt_reproj/"
local_dest = "C:/Users/Matthew Bonnema/Documents/dswx_data/mosaic/"

with open('dswx_manifest.txt') as f:
    lines = f.readlines()

print(lines[0])

cont = 'sa' # af,as,au,na,sa,eu
lvl = '01'

basin_path  = f'./shapefiles/basins/hybas_{cont}/hybas_{cont}_lev{lvl}_v1c.shp'
basin_gdf = gpd.read_file(basin_path)
#basin_gdf.head()

mrg_gdf = gpd.read_file('./shapefiles/world_mgrs/mgrs_region.shp') 
#mrg_gdf.head()

target_basin =  basin_gdf
grid_codes = gpd.sjoin(mrg_gdf,target_basin)
tile_list = []
for row in grid_codes.iterrows():
    tile_list.append(row[1].iloc[0]+row[1].iloc[1])
len(tile_list)

keys = []
for line in lines:
    prefix = line.split(bucket_name+'/')[-1][:-2]
    filename = prefix.split('/')[-1]+'_B01_WTR.tiff'
    tile = filename.split('_')[4][1:]
    if tile in tile_list:
        keys.append(filename)
len(keys)

i = 0
for key in keys[0:10]:
    print(f'{local_path}{key}')
    print(f'{local_reproj}{key[:-5]}')
    input_raster = gdal.Open(f'{local_path}{key}')
    dest_path = f'{local_reproj}{key}'
    kwargs = gdal.WarpOptions(dstSRS='ESPG:4326')
    #print(gdal.WarpOptions(dstSRS='ESPG:4326'))
    warp = gdal.Warp(destNameOrDestDS=dest_path,srcDSOrSrcDSTab=input_raster,options=gdal.WarpOptions(dstSRS='ESPG:4326'))
    #warp = None
    if i%100 == 0:
        print(f'Finshed reprojecting {i} tiles')
    i = i+1