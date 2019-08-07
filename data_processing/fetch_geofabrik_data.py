import pandas as pd
import time 
import typing

import os 
import sys 
import wget

# Paths
ROOT = "../"
BLOCK_PATH = os.path.join(ROOT, "data", "blocks")    # Africa
GEOJSON_PATH = os.path.join(ROOT, "data", "geojson") #"../data/geojson/Africa"
GADM_GEOJSON_PATH = os.path.join(ROOT, "data", "geojson_gadm") #"../data/geojson_gadm/Africa"
GEOFABRIK_PATH = os.path.join(ROOT, "data", "input")

TRANS_TABLE = pd.read_csv(os.path.join(ROOT, "data_processing", 'country_codes.csv'))


#http://download.geofabrik.de/africa/algeria-latest.osm.pbf
def urlexists_stream(uri: str) -> bool:
    try:
        with requests.get(uri, stream=True) as response:
            try:
                response.raise_for_status()
                return True
            except requests.exceptions.HTTPError:
                return False
    except requests.exceptions.ConnectionError:
        return False

def make_url(geo_name, geo_region):

    url = "http://download.geofabrik.de/{}/{}-latest.osm.pbf".format(geo_region, geo_name)

    if geo_name == "antarctica":
        url = "http://download.geofabrik.de/antarctica-latest.osm.pbf"

    elif geo_name == "puerto-rico":
        url = "http://download.geofabrik.de/north-america/us/puerto-rico-latest.osm.pbf"

    return url 

if __name__ == "__main__":

	names = TRANS_TABLE['geofabrik_name']
	regions = TRANS_TABLE['geofabrik_region']

	for geofabrik_name, geofabrik_region in zip(names, regions):

		outfile = geofabrik_name + "-latest.osm.pbf"

		# Check that we haven't already downloaded it
		output_path = os.path.join(GEOFABRIK_PATH, geofabrik_region.title())
		if os.path.isfile(os.path.join(output_path, outfile)):
			print("We have geofabrik data for {} -- see: {}".format(geofabrik_name, output_path))
			continue

	    url = make_url(n, r)

	    if uri_exists_stream(url):
	        wget.download(url, os.path.join(output_path, outfile))
	    else:
	        print("geofabrik_name = {} or geofabrik_region = {} are wrong".format(geofabrik_name, geofabrik_region))
	        continue

