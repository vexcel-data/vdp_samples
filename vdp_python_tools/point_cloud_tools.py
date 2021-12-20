
import pdal
import sys
sys.path
sys.path.append('C:\Python35\Lib\site-packages\laspy')
import numpy as np
import laspy
import json

from vdp_python_tools.tile_math import degrees_per_pixel, pixel_to_coord

def dsm_to_pointcloud(elevation_array, bounds, rgb_array = None):
    pixels_wide, pixels_high, _ = elevation_array.shape

    deg_per_pixel_wide, deg_per_pixel_high = degrees_per_pixel(bounds, pixels_wide, pixels_high)

    points_3d = []
    if rgb_array is not None:
        for p_x in range(pixels_wide):
            for p_y in range(pixels_high):
                x, y = pixel_to_coord(p_x, p_y, bounds, deg_per_pixel_wide, deg_per_pixel_high)
                z = elevation_array[p_y, p_x, 0]
                points_3d.append([x, y, z, *rgb_array[p_y, p_x]])
    else:
        for p_x in range(pixels_wide):
            for p_y in range(pixels_high):
                x, y = pixel_to_coord(p_y, p_x, bounds, deg_per_pixel_wide, deg_per_pixel_high)
                z = elevation_array[p_y, p_x, 0]
                points_3d.append([x, y, z])
    return points_3d


def write_point_cloud_data(xyz, filepath_point_cloud_name, zoom, color = False):
    # 1. Create a new header
    header = laspy.LasHeader(point_format=2, version="1.2")
    #header.add_extra_dim(laspy.ExtraBytesParams(name="random", type=np.int32))
    #header.scales = np.array([0.1, 0.1, 0.1])

    header.offset = [0, 0, 0] # could need to make this ground level from DTM
    header.scales = np.array([1, 1, 0.01])

    # 2. Create a Las
    las = laspy.LasData(header)

    las.x = xyz[:, 0]
    las.y = xyz[:, 1]
    las.z = xyz[:, 2]
    if color:
        las.red = xyz[:, 3]
        las.green = xyz[:, 4]
        las.blue = xyz[:, 5]
    #las.random = np.random.randint(-1503, 6546, len(las.points), np.int32)

    las.write(filepath_point_cloud_name)
    
    pipeline_config = [
        {
            "filename": filepath_point_cloud_name,
            "spatialreference":"EPSG:3857+3855"
        },
        {
            "type":"filters.reprojection",
            "in_srs":"EPSG:3857+3855",
            "out_srs":"EPSG:3857+3855"
        },
        {
            "filename": filepath_point_cloud_name
        }
    ]


    pipeline = pdal.Pipeline(json.dumps(pipeline_config))
    pipeline.execute()