import requests

import geopandas as gpd
from vdp_python_tools.authentication import login

# WA = wide area, this program captures 20cm GSD data
wa_layers = ["bluesky-high-europe", "bluesky-high"]
# UA = urban area, this program captures 7.5cm GSD data
ua_layers = ['bluesky-ultra',
    'bluesky-ultra-europe',
    'bluesky-ultra-g',
    'bluesky-ultra-oceania']

def create_coverage_dataframe(layers=None, print_urls=False, products=["ortho"], **kwargs):
    token = login()

    extra_params = ""
    if len(kwargs) > 0:
        extra_params += "&" + "&".join([f"{key}={value}" for key,value in kwargs.items()])

    raw_features = []
    if layers is None:
        layers = ua_layers + wa_layers
    for product in products:
        api_name = {"ortho": "OrthoCoverage", "dsm": "DSMCoverage", "dtm": "DTMCoverage"}[product]
        for layer_name in layers:
            url = f"https://api.gic.org/metadata/{api_name}/?token={token}&layer={layer_name}" + extra_params
            if print_urls:
                print(url.replace(token, "{token}"))
            r = requests.get(url) 
            raw_features += r.json().get('features', [])

    ortho_features = process_coverage_aoi_features(raw_features)
    gdf_existing_coverage = gpd.GeoDataFrame.from_features(ortho_features)
    return gdf_existing_coverage

def process_coverage_aoi_features(features):
    """
    This function is used to pull the child AOIs out of their parents to flatten the nested data into a flat set of features
    """
    ortho_features = []

    for feature in features:
        children = feature.get("Child AOI", [])
        if len(children) < 1:
            ortho_features.append(feature)
        else:
            ortho_features.extend([child_to_feature(child, feature) for child in children])
    return ortho_features


def child_to_feature(child, parent):
    feature = {"geometry": child['Coverage']}
    del child['Coverage']
    feature["properties"] = child
    feature["properties"]["layer"] = parent["properties"]["layer"]
    feature["properties"]["Coverage Type"] = parent["properties"]["Coverage Type"]
    return feature