import folium

def visualize_geometry_on_map(geometry, zoom = 19):
    lon, lat = geometry.centroid.coords[0]
    m = folium.Map(location=[lat, lon], tiles="cartodbpositron", zoom_start=zoom)

    folium.GeoJson(
        geometry,
    ).add_to(m)
    return m