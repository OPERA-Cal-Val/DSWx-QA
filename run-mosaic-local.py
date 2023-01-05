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


bucket_name = 'opera-pst-rs-pop1'
local_path = "C:/Users/Matthew Bonnema/Documents/dswx_data/wtr/"
local_dest = "C:/Users/Matthew Bonnema/Documents/dswx_data/mosaic/"

with open('dswx_manifest.txt') as f:
    lines = f.readlines()

cont = 'na' # af,as,au,na,sa,eu
lvl = '03'


basin_path  = f'./shapefiles/basins/hybas_{cont}/hybas_{cont}_lev{lvl}_v1c.shp'
basin_gdf = gpd.read_file(basin_path)
mrg_gdf = gpd.read_file('./shapefiles/world_mgrs/mgrs_region.shp') 

def make_mosaic(basinID):
    try:
        mosaics_list = os.listdir(local_dest)

        if f'{cont}_basin{basinID}_WTR.tif' in mosaics_list:
            print(f'mosaic alreaddy exists for basin {basinID}')
            return
        target_basin =  basin_gdf[basin_gdf.PFAF_ID==basinID]
        grid_codes = gpd.sjoin(mrg_gdf,target_basin)
        
        tile_list = []
        for row in grid_codes.iterrows():
            tile_list.append(row[1].iloc[0]+row[1].iloc[1])
        
        keys = []
        for line in lines:
            prefix = line.split(bucket_name+'/')[-1][:-2]
            filename = prefix.split('/')[-1]+'_B01_WTR.tiff'
            tile = filename.split('_')[4][1:]
            if tile in tile_list:
                keys.append(filename)
        
        if len(keys) == 0:
            print(f'no prodducts found for basin: {basinID}')
        elif f'{cont}_basin{basinID}_WTR.tif' in mosaics_list:
            print(f'mosaic alreaddy exists for basin {basinID}')
        else:
            ds_to_mosaic = []
            i = 0
            for key in keys:
                file_path = f'{local_path}{key}'
                xds = rioxarray.open_rasterio(file_path,cache=False)
                reproj = xds.rio.reproject("EPSG:4326")
                ds_to_mosaic.append(reproj)
                xds.close()
                reproj.close()
                del xds
                del  reproj

            merged_raster =  merge_arrays(dataarrays = ds_to_mosaic, crs="EPSG:4326", nodata = 255)
            merged_raster.rio.to_raster(f'{local_dest}{cont}_basin{basinID}_WTR.tif', tiled=True, windowed=True)
            merged_raster.close()
            del merged_raster
            print(f'completed mosaic for basin {basinID}')
    except Exception as e:
        print(f'failed to make mosaic for basin {basinID}, error: {e}')

for row in basin_gdf.iterrows():
    ID = row[1]['PFAF_ID']
    make_mosaic(ID)

