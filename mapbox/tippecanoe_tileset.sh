
# Set destination directory
cd /project2/bettencourt/mnp/prclz/data/tilesets

tippecanoe -o full_zoom.mbtiles --force --attribute-type=complexity:int \
  --minimum-zoom=0 --maximum-zoom=13 -P \
  --coalesce-smallest-as-needed \
  /project2/bettencourt/mnp/prclz/data/tilesets/global_file.geojson

# Join zoom levels
# tile-join -o zoom_combined.mbtiles --force zoom1.mbtiles zoom2.mbtiles
