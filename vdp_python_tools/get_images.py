import requests
import shutil
import numpy as np
import shutil
import io
import os


import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from osgeo import gdal
from pyproj import CRS
from PIL.Image import UnidentifiedImageError
from PIL import Image

from vdp_python_tools.tile_math import deg2num, num2deg, tiles_in_polygon
from vdp_python_tools.authentication import login

token = login()


def georeference_raster_tile(x, y, zoom, path, epsg = 4326):
    w, s = num2deg(x, y, zoom) 
    e, n = num2deg(x+1, y+1, zoom)
    
    filename, extension = os.path.splitext(path)
    gdal.Translate(filename + '.tif',
                   path,
                   outputSRS=f'EPSG:{epsg}',
                   outputBounds=[w, s, e, n])

    return filename + '.tif'

def download_and_mosaic_in_geometry(aoi_geometry, zoom, image_type, output_folder, output_epsg):
    """
    zoom: 16-20 for bluesky-high, 16-21 for bluesky-ultra
    """
    imagery_type = image_type.lower()

    if zoom == 21 and imagery_type == "ortho":
        imagery_type = "ortho-urban-area"
    elif imagery_type == "ortho":
        imagery_type = "ortho-high-area"

    try:
        api = {
            "dsm": "GetDSMTile",
            "ortho-high-area": "GetOrthoImageTile/bluesky-high",
            "ortho-urban-area": "GetOrthoImageTile/bluesky-ultra"
        }[image_type]
    except KeyError:
        raise Exception("imagery-type needs to be either dsm, ortho-high-area, or ortho-urban-area")
    
    format_type = {
        "dsm": "tif",
        "ortho-urban-area": "png",
        "ortho-high-area": "png"
    }[image_type]
    
    tile_coords = tiles_in_polygon(aoi_geometry, zoom)
    print(f"Running {len(tile_coords)} requests to download {len(tile_coords)*256e3/1e9}Gb of data...")
    shutil.rmtree(f"{output_folder}", ignore_errors=True)
    os.makedirs(f"{output_folder}", exist_ok=True)

    
    rasters_to_merge = []
    for x, y, zoom in tile_coords:
        url = f"https://api.vexcelgroup.com/images/{api}/{zoom}/{x}/{y}?token={token}"
        if format_type != "tif":
            url += f"&format={format_type}"
        response = requests.get(url, stream = True)
        if response.reason != "OK":
            raise Exception(f"API failed to get tile from api {api} at x={x} y={y} zoom={zoom} see url below \n {url}")
        filepath = os.path.join(output_folder, f"{image_type}_img_{zoom}_{x}_{y}.{format_type}")
        with open(filepath, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
            
        if image_type in ["ortho-urban-area", "ortho-high-area"]: # then the tiles aren't georeferenced...yet
            filepath_translated_tile = georeference_raster_tile(x, y, zoom, filepath)
            os.remove(filepath)
            rasters_to_merge.append(filepath_translated_tile)
        else: 
            rasters_to_merge.append(filepath)
    print(f"...finished downloading data")

    src_files_to_mosaic = []
    for filepath in rasters_to_merge:
        src = rasterio.open(filepath)
        src_files_to_mosaic.append(src)
        
    mosaic, out_trans = merge(src_files_to_mosaic)
    
    crs = CRS.from_epsg(3857)
    out_meta = src.meta.copy()

    # Update the metadata
    out_meta.update({"driver": "GTiff",
      "height": mosaic.shape[1],
      "width": mosaic.shape[2],
      "transform": out_trans,
      "crs": crs.to_string(), # Insert own CRS here
    })

    filepath_mosaic = f"{output_folder}/mosaic.tif"

    with rasterio.open(filepath_mosaic, "w", **out_meta) as dest:
        dest.write(mosaic)

    if output_epsg == 4326:
        return # no more to do

    dst_crs = f'EPSG:{output_epsg}'

    with rasterio.open(filepath_mosaic) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(filepath_mosaic.replace("mosaic.tif", f"mosaic_{output_epsg}.tif"), 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)


def write_tile_from_api(x, y, zoom, output_filepath, token, api="GetOrthoImageTile/bluesky-ultra", api_parameters = ""):
        url = f"https://api.vexcelgroup.com/images/{api}/{zoom}/{x}/{y}?token={token}" + api_parameters
        response = requests_get_with_catch(url, stream = True)
        try:
            with open(output_filepath, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
        except UnidentifiedImageError:
            print("Tile failed to download", url)
            return response
                
import math
import time

def requests_get_with_catch(url, **kwargs):
    try:
        return requests.get(url, **kwargs)
    except ConnectionError:
        time.sleep(5)
        return request_get_with_catch(url, **kwargs)

def get_dsm_image(polygon_bbox_lat_lon, token):
    bbox_in_tile_numbers = [*deg2num(*polygon_bbox_lat_lon[:2], 21), *deg2num(*polygon_bbox_lat_lon[2:], 21)]
    image_array = get_image_from_tile_api(bbox_in_tile_numbers, 21, token, api="GetDSMTile")
    return Image.fromarray(image_array)

def get_dtm_image(polygon_bbox_lat_lon, token):
    bbox_in_tile_numbers = [*deg2num(*polygon_bbox_lat_lon[:2], 20), *deg2num(*polygon_bbox_lat_lon[2:], 20)]
    image_array = get_image_from_tile_api(bbox_in_tile_numbers, 20, token,  api="GetDTMTile")
    return Image.fromarray(image_array)
    
def get_rgb_image(polygon_bbox_lat_lon, token, zoom=21):
    bbox_in_tile_numbers = [*deg2num(*polygon_bbox_lat_lon[:2], zoom), *deg2num(*polygon_bbox_lat_lon[2:], zoom)]
    image_array = get_image_from_tile_api(bbox_in_tile_numbers, zoom, token)
    return Image.fromarray(image_array)

def get_nir_image(polygon_bbox_lat_lon, token):
    bbox_in_tile_numbers = [*deg2num(*polygon_bbox_lat_lon[:2], 21), *deg2num(*polygon_bbox_lat_lon[2:], 21)]
    image_array = get_image_from_tile_api(bbox_in_tile_numbers, 21, token, api = "GetOrthoImageTile/bluesky-ultra", api_parameters = "&renderingRule=nir")
    return Image.fromarray(image_array)

def get_image_from_tile_api(bbox_in_tile_numbers, zoom, token, api="GetOrthoImageTile/bluesky-ultra", api_parameters = ""):
    if api == "GetDSMTile": assert zoom == 21 # The DSM is only available for our 7.5cm product and we don't down sample
    if api == "GetDTMTile": assert zoom == 20 # The DTM is only available for our 20cm product 
        
    x_tiles = list(range(bbox_in_tile_numbers[0], bbox_in_tile_numbers[2] + 1))
    y_tiles = list(range(bbox_in_tile_numbers[3], bbox_in_tile_numbers[1] + 1))

    n_x_tiles = len(x_tiles)
    n_y_tiles = len(y_tiles)

    image_array = np.zeros([n_y_tiles*256, n_x_tiles*256], dtype="uint8") if api in ["GetDSMTile", "GetDTMTile"] else np.zeros([n_y_tiles*256, n_x_tiles*256, 4], dtype="uint8")


    for i_x, x in enumerate(x_tiles):
        for i_y, y in enumerate(y_tiles):
            url = f"https://api.vexcelgroup.com/images/{api}/{zoom}/{x}/{y}?token={token}" + api_parameters
            
            try:
                if api == "GetDSMTile" or api == "GetDTMTile":
                    response = requests_get_with_catch(url)
                    image = Image.open(io.BytesIO(response.content))
                else:
                    response = requests_get_with_catch(url, stream = True)
                    image = Image.open(response.raw)
            except UnidentifiedImageError:
                print("womp womp", url)
                return response
                
            image_array[ i_y*256:(i_y+1)*256, i_x*256:(i_x+1)*256] = np.array(image)
            
    return image_array

def get_tile(x, y, zoom, api, token, layer="bluesky-ultra", **kwargs):
    """
    For background on how tiles are named according to x, y and zoom, see 
    https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames

    For more detail on each of the parameters below, see our documenation 
    https://vexcel.atlassian.net/wiki/spaces/APIDOCS/pages/2131887188/GetOrthoImageTile+Service+-+v1.4#Parameters

    :param x: The x coordinate of the tile. (Datum: WGS84)
    :param y: The y coordinate of the tile. (Datum: WGS84)
    :param zoom: The zoom level of the tile. 
    :param api: the API endpoint
    :param layer: the name of the layer
    :param kwargs: optional keyword arguments to be passed directly into the API call
    :returns: this is a description of what is returned
    """

    if api == "GetDSMTile" or api == "GetDTMTile": 
        url = f"https://api.vexcelgroup.com/images/{api}/{zoom}/{x}/{y}?token={token}"
        url += f"&layer={layer}"
        if len(kwargs) > 0:
            url += "&" + "&".join([f"{k}={v}" for k, v in kwargs.items()])
        response = requests.get(url)
        image = Image.open(io.BytesIO(response.content))
    else:
        url = f"https://api.vexcelgroup.com/images/{api}/{layer}/{zoom}/{x}/{y}?token={token}" 
        if len(kwargs) > 0:
            url += "&" + "&".join([f"{k}={v}" for k, v in kwargs.items()])
        response = requests.get(url, stream = True)
        image = Image.open(response.raw)
    return image