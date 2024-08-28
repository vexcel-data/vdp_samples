#This code utilizes Pulling Tiles for a Large Area script and incorporates the use of threading so it will download faster, make sure to update with your token and paths where indicated
# Also, check the zoom level, file format, etc. to make sure you are downloading the tiles how you would like
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

#UPDATE WITH YOUR TOKEN
vexceltoken = 'your token here'

tile_size = 256   #WMTS tiles are always 256 pixels square
zoom_level = 21  #standard WMTS zoom level from 1 to 21

#start with a single polygon in decimal degrees
wkt_polygon = 'POLYGON ((-84.9216897529607 39.303109024421, -84.9208746877385 39.3030944654052, -84.9208741512854 39.3023645309455, -84.9210559991123 39.2994309522366, -84.9175271479616 39.2993837323995, -84.9162206095455 39.2985746143958, -84.9125656812659 39.2971575165982, -84.9124895158145 39.2977624853732, -84.9120864837574 39.2978608960028, -84.9118579972831 39.2976798955032, -84.9118577803764 39.296811048749, -84.909898899836 39.2973551316311, -84.9095742662328 39.2973295501389, -84.9094100882759 39.2971104485323, -84.9095417180295 39.2968784613033, -84.9119427187733 39.2962002736588, -84.9118595956151 39.2950792197535, -84.9119823605597 39.2948190927549, -84.911045538302 39.2947269779418, -84.9095313892921 39.2925041743974, -84.9084204330788 39.2930327002325, -84.9076736877116 39.2930976689601, -84.9073688342226 39.2930073110452, -84.907394360284 39.292612924329, -84.9082118596529 39.292491167149, -84.9091316469297 39.292039912958, -84.9076534202781 39.2910160450119, -84.9064805026177 39.290418058304, -84.8995812631789 39.2903135545364, -84.8991452566478 39.2901499336912, -84.8986135563299 39.2897004504246, -84.8982057462366 39.2913215429169, -84.8978328726347 39.2914757994454, -84.8975268315629 39.2911605559221, -84.8980109048884 39.2893659209912, -84.8965909896678 39.2894111420108, -84.8962846209451 39.2890960961359, -84.8965776391336 39.2888596650451, -84.898622144538 39.2888498871455, -84.8997041308813 39.2897546783053, -84.9010257191315 39.289706776654, -84.9026756842741 39.2898366236333, -84.9026892406516 39.2881451046051, -84.9031412949595 39.2879647456838, -84.9033906332519 39.2882297077166, -84.9033943337911 39.2898255694665, -84.9041197225021 39.2896509573605, -84.9043785518117 39.2897733794443, -84.905926332306 39.2898522237189, -84.9063192473094 39.2896974446333, -84.908618701195 39.2909250576732, -84.9093394949203 39.2906981184535, -84.9096645494231 39.2907199648375, -84.909779356103 39.2911046411348, -84.9092307670535 39.291334902731, -84.9103572638266 39.2924221868749, -84.9118396554956 39.2903746936919, -84.9117091772251 39.2876653751623, -84.9119372708164 39.2862119108017, -84.9118142193856 39.2859642388028, -84.9119354706285 39.2856348585656, -84.9123502611327 39.2855728660039, -84.9126759897857 39.2861263088524, -84.9124875443021 39.2869009022789, -84.9124346723825 39.2884476862846, -84.9125514942865 39.2905125625759, -84.9127963448422 39.2908199247318, -84.9120331057471 39.2912471476883, -84.9107737350174 39.2930536770332, -84.9115613089751 39.2942653249913, -84.9124200020158 39.2942604579, -84.9126616211312 39.2944308417548, -84.9126589998526 39.2964561163806, -84.9127727512431 39.296615421576, -84.9155597528042 39.297648992525, -84.9171242929141 39.2984241917993, -84.9165193979341 39.2969818448314, -84.9165242080229 39.2960877660401, -84.9169744391556 39.2959045940538, -84.9172077130684 39.2960818655826, -84.9172374865217 39.2969336722204, -84.9180447015273 39.2988464940529, -84.9195407373154 39.2988641779422, -84.9198694114548 39.2987455954685, -84.9201214986947 39.2988637851585, -84.9211838604579 39.2988748408932, -84.9212751697683 39.2985430229459, -84.921683295153 39.2984582104658, -84.9219132284773 39.2987335864207, -84.9217580716176 39.3002392180002, -84.9261566526299 39.3002626873169, -84.9265000973668 39.3004538529311, -84.9264512021082 39.3007045240167, -84.9261614464329 39.3008211301771, -84.9217439885824 39.3007975660723, -84.9216897529607 39.303109024421))'
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
#This code will go through all the intersecting tiles and download the zoom level 20 DSM data from our bluesky-high layer and save them to a list to be merged into a single mosaic later
rasters_to_merge = []
image_type = "ultra-area"

#WILL NEED TO UPDATE FOLDER LOCATIONS
output_dir = "update me"
#print all of the intersecting tile addresses, the URL to return the image tile, and the URL to return the DSM tile
# Number of threads to use
num_threads = 10
urls = []
filenames = []
filepaths = []
for i in tile_addresses:
    url = f"https://api.gic.org/images/GetOrthoImageTile/bluesky-ultra/{i.z}/{i.x}/{i.y}?token={vexceltoken}"
    urls.append(url)
    filenames.append(f"{image_type}_img_{i.z}_{i.x}_{i.y}.png")
    filepath = os.path.join(output_dir, f"{image_type}_img_{i.z}_{i.x}_{i.y}.png")
    filepaths.append(filepath)

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

tileCount = 0 
for i in tile_addresses:
    filepath_translated_tile = georeference_raster_tile(i.x, i.y, i.z, filepaths[tileCount])
    os.remove(filepaths[tileCount])
    tileCount = tileCount + 1



#This code will read all the DSM tiles downloaded and merge them together into a single mosaic
from rasterio.plot import show
from rasterio.merge import merge
import rasterio as rio
from pathlib import Path

#WILL NEED TO UPDATE FOLDER LOCATIONS
path = Path(r'update me')
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
