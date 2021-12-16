import math
from shapely.geometry import box as geometry_from_bounding_box
import geopandas as gpd

def get_tile_boundary(x, y, zoom):
    w, s = num2deg(x, y, zoom)
    e, n = num2deg(x+1, y+1, zoom)
    tile_boundary = geometry_from_bounding_box(w, s, e, n)
    return tile_boundary

def tiles_in_polygon(geometry, zoom, tile_footprint_filepath=None):
    w, n, e, s = geometry.bounds
    minx, miny = deg2num(w, s, zoom)
    maxx, maxy = deg2num(e, n, zoom)
    tiles = []
    geometries = []
    for x in range(minx, maxx):
        for y in range(miny, maxy):
            tile_boundary = get_tile_boundary(x, y, zoom)
            if tile_boundary.intersects(geometry):
                tiles.append((x, y, zoom))
                geometries.append(tile_boundary)
    if tile_footprint_filepath:
        gpd.GeoDataFrame(geometry=geometries).to_file(tile_footprint_filepath)
    return tiles

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)

def deg2num(lon_deg, lat_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def degrees_per_pixel(bounds, pixels_wide, pixels_high):
    width_in_deg = bounds[2] - bounds[0]
    height_in_deg = bounds[3] - bounds[1]

    deg_per_pixel_wide = width_in_deg/pixels_wide
    deg_per_pixel_high = height_in_deg/pixels_high
    return deg_per_pixel_wide, deg_per_pixel_high

def pixel_to_coord(p_x, p_y, bounds, deg_per_pixel_wide, deg_per_pixel_high):
    c_x = bounds[0] + p_x*deg_per_pixel_wide
    c_y = bounds[1] + p_y*deg_per_pixel_high
    return [ c_x, c_y]

def coord_to_pixel(c_x, c_y, bounds, deg_per_pixel_wide, deg_per_pixel_high, pixels_wide, pixels_high):
    p_x = int((c_x - bounds[0])/deg_per_pixel_wide)
    p_y = int((c_y - bounds[1])/deg_per_pixel_high)
    return [p_x, pixels_high - p_y]

