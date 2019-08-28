
# Set directory
cd /project2/bettencourt/mnp/prclz/data/mapbox_test

# Create list of all geojson files in input directory
complexity_list=()
for i in /project2/bettencourt/mnp/prclz/data/mapbox_test/SLE_GEOJSON/*.geojson; do
    complexity_list+=("$i")
done
echo "${complexity_list[@]}"
mapbox_input=${complexity_list[@]}
echo ${mapbox_input}

# Convert geojson to mbtile object at zoom level 1 object
tippecanoe -o mapbox_output/sle_zoom1.mbtiles --force --exclude=centroids_multipoint  \
	--minimum-zoom=0 --maximum-zoom=10 -P \
	--coalesce-densest-as-needed --coalesce-smallest-as-needed --extend-zooms-if-still-dropping \
	${mapbox_input}

# Convert geojson to mbtile object at zoom level 2 object
tippecanoe -o mapbox_output/sle_zoom2.mbtiles --force --exclude=centroids_multipoint  \
	--minimum-zoom=10 --maximum-zoom=13 -P \
	--coalesce-densest-as-needed --coalesce-smallest-as-needed --extend-zooms-if-still-dropping \
	${mapbox_input}

# Join mbtiles together to allow differing zooms at different layers
tile-join -o mapbox_output/sle_zoom_combined.mbtiles --force mapbox_output/sle_zoom1.mbtiles mapbox_output/sle_zoom2.mbtiles
