
# Convert geojson to mbtile object at zoom level 1 object
tippecanoe -o zoom1.mbtiles --force --exclude=centroids_multipoint --attribute-type=complexity:int \
	--minimum-zoom=0 --maximum-zoom=10 -P  \
	--coalesce-densest-as-needed --coalesce-smallest-as-needed --extend-zooms-if-still-dropping \
	${COMPLEXITY_GEOJSON_FILEPATH}

# Convert geojson to mbtile object at zoom level 2 object
tippecanoe -o zoom2.mbtiles --force --exclude=centroids_multipoint --attribute-type=complexity:int \
	--minimum-zoom=10 --maximum-zoom=13 -P \
	--coalesce-densest-as-needed --coalesce-smallest-as-needed --extend-zooms-if-still-dropping \
	${COMPLEXITY_GEOJSON_FILEPATH}
	
# Join zoom levels
tile-join -o zoom_combined.mbtiles --force zoom1.mbtiles zoom2.mbtiles
