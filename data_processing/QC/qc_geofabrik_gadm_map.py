import pandas as pd
import time 

import os 
import sys 

# Paths
ROOT = "../"
BLOCK_PATH = os.path.join(ROOT, "data", "blocks")    # Africa
GEOJSON_PATH = os.path.join(ROOT, "data", "geojson") #"../data/geojson/Africa"
GADM_PATH = os.path.join(ROOT, "data", "GADM")
GADM_GEOJSON_PATH = os.path.join(ROOT, "data", "geojson_gadm") #"../data/geojson_gadm/Africa"
GEOFABRIK_PATH = os.path.join(ROOT, "data", "input")

TRANS_TABLE = pd.read_csv(os.path.join(ROOT, "data_processing", 'country_codes.csv'))

'''
Just a very simple script to make sure that we have a GADM bounds file correctly 
mapped, for each global south country in TRANS_TABLE from geofabrik --> GADM
'''

if __name__ == "__main__":

	TRANS_TABLE = TRANS_TABLE[ TRANS_TABLE['geofabrik_NA']!=1 ]

	for gadm_name in TRANS_TABLE['gadm_name']:

		if os.path.isdir(os.path.join(GADM_PATH, gadm_name)):
			continue
		else:
			print("Country code {} has no GADM file".format(gadm_name))