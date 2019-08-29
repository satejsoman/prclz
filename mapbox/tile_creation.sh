
# Concatenate files
cat /project2/bettencourt/mnp/prclz/data/mapbox_test/SLE_GEOJSON/*.geojson > /project2/bettencourt/mnp/prclz/data/mapbox_test/all_gadms.geojson

# Convert geojson to mbtile object at zoom level 1 object
tippecanoe -o /project2/bettencourt/mnp/prclz/data/mapbox_test/mapbox_output/sle_zoom1.mbtiles --force --exclude=centroids_multipoint --attribute-type=complexity:int \
	--minimum-zoom=0 --maximum-zoom=10 -P  \
	--coalesce-densest-as-needed --coalesce-smallest-as-needed --extend-zooms-if-still-dropping \
	/project2/bettencourt/mnp/prclz/data/mapbox_test/all_gadms.geojson

# Convert geojson to mbtile object at zoom level 2 object
tippecanoe -o /project2/bettencourt/mnp/prclz/data/mapbox_test/mapbox_output/sle_zoom2.mbtiles --force --exclude=centroids_multipoint --attribute-type=complexity:int \
	--minimum-zoom=10 --maximum-zoom=13 -P \
	--coalesce-densest-as-needed --coalesce-smallest-as-needed --extend-zooms-if-still-dropping \
	/project2/bettencourt/mnp/prclz/data/mapbox_test/all_gadms.geojson

tile-join -o /project2/bettencourt/mnp/prclz/data/mapbox_test/mapbox_output/sle_zoom_combined.mbtiles --force /project2/bettencourt/mnp/prclz/data/mapbox_test/mapbox_output/sle_zoom1.mbtiles /project2/bettencourt/mnp/prclz/data/mapbox_test/mapbox_output/sle_zoom2.mbtiles


scp nmarchio@midway.rcc.uchicago.edu:/project2/bettencourt/mnp/prclz/data/mapbox_test/mapbox_output/sle_zoom_combined.mbtiles /Users/nmarchio/Desktop

