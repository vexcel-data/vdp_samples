
"""Params"""
filepath_boundary = f"C:/Users/PatrickEdwards/Downloads/California_Work_Units.zip"
filepath_output = "./data/tmp/Test1"
imagery_type = "ortho"
zoom = 16
@click.command()
@click.option('--filepath-boundary', required=True, help='The location of a shapefile OR a zipped folder containing shapefile and associated .dbf, .shx and .prj')
@click.option('--filepath-output', required=True, help='The folder where the mosaiced tiles will be written')
@click.option('--imagery-type', required=True, type=click.Choice(['ortho-high-area', 'ortho-urban-area', 'dsm'], case_sensitive=False), help="Either 'ortho-high-area', 'ortho-urban-area' or 'dsm'. ortho-high-area is only available at zoom level 16-20 and has a GSD of 20cm or better.")
@click.option('--zoom', required=True, type=click.Choice(["16", "17", "18", "19", "20", "21"], case_sensitive=False), help='Zoom level (16-20) of map tiles used')
@click.option('--output-epsg', required=False, help='EPSG for the coordinates of the bounds of the output raster file')
def download_and_mosaic_in_shapefile(filepath_boundary, filepath_output, imagery_type, zoom, output_epsg=4326):
    zoom = int(zoom)
    gdf = gpd.read_file(filepath_boundary)
    gdf.geometry = gdf.geometry.to_crs(epsg=4326) 

    aoi_geometry = gdf.dissolve().iloc[0].geometry
    download_and_mosaic_in_geometry(aoi_geometry, zoom, imagery_type, filepath_output, output_epsg)
    
if __name__ == '__main__':
    download_and_mosaic_in_shapefile()

# python mosaic_tiles_in_shapefile.py --filepath-boundary "Halff_4326.shp" --filepath-output "./output" --imagery-type ortho --zoom 17