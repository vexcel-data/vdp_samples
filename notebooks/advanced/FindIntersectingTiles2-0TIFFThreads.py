from shapely.geometry import Polygon
from shapely.wkt import loads
import math
from math import pi, atan, sinh
import requests
import os
import shutil
from osgeo import gdal
import concurrent.futures

#function to find the geographic bounds of an individual WMTS tile.
def tile_bounds(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_left = xtile / n * 360.0 - 180.0
    lat_top = atan(sinh(pi * (1 - 2 * ytile / n))) * 180.0 / pi
    lat_bottom = atan(sinh(pi * (1 - 2 * (ytile + 1) / n))) * 180.0 / pi
    return lon_left, lat_bottom, lon_left + 360.0 / n, lat_top

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)

def georeference_raster_tile(x, y, zoom, path, epsg = 4326):
    w, s = num2deg(x, y, zoom) 
    e, n = num2deg(x+1, y+1, zoom)
    
    filename, extension = os.path.splitext(path)
    gdal.Translate(filename + '.tif',
                   path,
                   outputSRS=f'EPSG:{epsg}',
                   outputBounds=[w, s, e, n])

    return filename + '.tif'

def download_file(url, filename):
    try:
        response = requests.get(url, stream = True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
                print(f"Downloaded {url} to {filename}")
        else:
            print(f"Failed to download {url}: Status code {response.status_code}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")


#class to represent a tile address
class tileAddress:
    def __init__(self, z, x, y):
        self.z = z
        self.x = x
        self.y = y


vexceltoken = 'yourtokenhere'

tile_size = 256   #WMTS tiles are always 256 pixels square
zoom_level = 20 #standard WMTS zoom level from 1 to 21

#start with a single polygon in decimal degrees
wkt_polygon = 'POLYGON Here'
polygon = loads(wkt_polygon)

#get the bounds (envelope or minimum bounding rectangle) in degrees
#this envelope represents the universe of tiles that we will test to see if they intersect the target Polygon
minx, miny, maxx, maxy = polygon.bounds
print(f"polygon bounds: {polygon.bounds} ")

#calculate the min and max tile addresses corresponding to the polygon bounds
n = 2 ** zoom_level
minx_tile2 = int((minx + 180.0) / 360.0 * n)
lat_rad = math.radians(miny)
maxy_tile2 = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

maxx_tile2 = int((maxx + 180.0) / 360.0 * n)
lat_rad = math.radians(maxy)
miny_tile2 = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

print (f"tile bounds: {minx_tile2}, {miny_tile2}, {maxx_tile2},  {maxy_tile2}\n" )

#iterate over each tile in the envelope and test to see if it intersects the target polygon
#if it does, we will add it to a list of tile addresses that we can use to request the DSM or imagery for that tile
tile_addresses = []
for x in range(minx_tile2, maxx_tile2 + 1):
    for y in range(miny_tile2, maxy_tile2 + 1):
        #get the bounds of this tile in degrees
        lon_left, lat_bottom, lon_right, lat_top = tile_bounds(x, y, zoom_level)

        #create a polygon in degrees for this tile
        tile_polygon = Polygon([
            (lon_left, lat_top),
            (lon_right, lat_top),
            (lon_right, lat_bottom),
            (lon_left, lat_bottom),
        ])

        #does this tile polygon intersect our target polygon? if so, add it to the list
        if tile_polygon.intersects(polygon):
            tile_addresses.append(tileAddress(zoom_level, x, y))
          
size = len(tile_addresses)
print("Number of tiles: " + str(size))
#This code will go through all the intersecting tiles and download the zoom level 20 DSM data from our wide-area layer or 21 from urban and save them to a list to be merged into a single mosaic later
rasters_to_merge = []
image_type = "wide-area"
#WILL NEED TO UPDATE FOLDER LOCATIONS
output_dir = "Folder Name"
#print all of the intersecting tile addresses, the URL to return the image tile, and the URL to return the DSM tile
# Number of threads to use
num_threads = 15
urls = []
filenames = []
#if long-term token use api_key instead of token
for i in tile_addresses:
    url = f"https://api.vexcelgroup.com/v2/dsm/tile?layer=wide-area&zoom={i.z}&tile-x={i.x}&tile-y={i.y}&bands=rgb&image-format=tiff&token={vexceltoken}"
    #url = f"https://api.vexcelgroup.com/v2/ortho/tile?layer=urban&zoom={i.z}&tile-x={i.x}&tile-y={i.y}&bands=rgb&image-format=tiff&api_key={vexceltoken}"
    urls.append(url)
    filenames.append(f"{image_type}_img_{i.z}_{i.x}_{i.y}.tif")

count = 0

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Submitting tasks to executor
    futures = []
    for url in urls:
        filename = os.path.join(output_dir, os.path.basename(filenames[count]))
        futures.append(executor.submit(download_file, url, filename))
        count = count + 1
        

    # Waiting for all tasks to complete
    for future in concurrent.futures.as_completed(futures):
        # Retrieve results of tasks
        future.result()

print("All downloads completed")



#This code will read all the DSM tiles downloaded and merge them together into a single mosaic
from rasterio.plot import show
from rasterio.merge import merge
import rasterio as rio
from pathlib import Path

#WILL NEED TO UPDATE FOLDER LOCATIONS
path = Path(r'FOLDER')
Path('output').mkdir(parents=True, exist_ok=True)
output_path = 'output/mosaic_output.tif'

raster_files = list(path.iterdir())
raster_to_mosiac = []

for p in raster_files:
    raster = rio.open(p)
    raster_to_mosiac.append(raster)

mosaic, output = merge(raster_to_mosiac)

output_meta = raster.meta.copy()
output_meta.update(
    {"driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": output,
    }
)

with rio.open(output_path, 'w', **output_meta) as m:
    m.write(mosaic)