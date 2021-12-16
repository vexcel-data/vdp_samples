from pyproj import Geod 

GEOD = Geod(ellps="WGS84")

def area_sq_m_wgs84(geometry):
    area = abs(GEOD.geometry_area_perimeter(geometry)[0])
    return area