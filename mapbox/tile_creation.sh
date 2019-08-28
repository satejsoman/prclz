
# Create list of all geojson files in input directory
complexity_list=()
for i in data/complexity/Africa/SLE/*.geojson; do
    complexity_list+=("$i")
done

# Convert to string
mapbox_input=${complexity_list[@]}
echo ${mapbox_input}

# Convert geojson to mbtile object at zoom level 1 object
tippecanoe --minimum-zoom=0 --maximum-zoom=10 -o sle_zoom1.mbtiles \
	-P --coalesce-densest-as-needed --coalesce-smallest-as-needed --extend-zooms-if-still-dropping \
	${mapbox_input}

# Convert geojson to mbtile object at zoom level 2 object
tippecanoe --minimum-zoom=10 --maximum-zoom=13-o sle_zoom2.mbtiles \
	-P --coalesce-densest-as-needed --coalesce-smallest-as-needed --extend-zooms-if-still-dropping \
	${mapbox_input}

# Join mbtiles together
tile-join -o sle_zoom1.mbtiles sle_zoom2.mbtiles

