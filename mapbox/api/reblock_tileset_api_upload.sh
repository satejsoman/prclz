
# CONVERT TO GEOJSON LINE DELIMITED
module load udunits/2.2
module load gdal/2.4.1 

cd /project2/bettencourt/mnp/prclz/data/tilesets
rm /project2/bettencourt/mnp/prclz/data/tilesets/reblock_file.geojson.ld
ogr2ogr -f "GeoJSONSeq" reblock_file.geojson.ld /project2/bettencourt/mnp/prclz/data/KEN_opt_path.geojson 


# SET PARAMETERS
MAPBOX_API_TOKEN=(::MAPBOX_API_TOKEN::)
MAPBOX_USERNAME=(nmarchi0)
TILESET_NAME=(reblock_file_$(date '+%Y%m%d'))
COMPLEXITY_GEOJSON_FILEPATH=(/project2/bettencourt/mnp/prclz/data/tilesets/reblock_file.geojson.ld)
JSON_RECIPE_TEMPLATE=(/project2/bettencourt/mnp/prclz/mapbox/api/zoom_reblock_recipe.json)

# FILL IN JSON RECIPE TEMPLATE
JSON_RECIPE_FILEPATH=(/project2/bettencourt/mnp/prclz/data/tilesets/mapbox_reblock_recipe.json)
sed -e "s/::MAPBOX_USERNAME::/${MAPBOX_USERNAME}/g" -e "s/::TILESET_NAME::/${TILESET_NAME}/g" < ${JSON_RECIPE_TEMPLATE} > ${JSON_RECIPE_FILEPATH}

# DELETE TILESET SOURCE ID (TO OVERWRITE EXISTING TILESET)
# curl -X DELETE "https://api.mapbox.com/tilesets/v1/sources/${MAPBOX_USERNAME}/${TILESET_NAME}?access_token=${MAPBOX_API_TOKEN}"

# UPLOAD AND CREATE GEOJSON SOURCE ID
curl -F file=@${COMPLEXITY_GEOJSON_FILEPATH} \
  "https://api.mapbox.com/tilesets/v1/sources/${MAPBOX_USERNAME}/${TILESET_NAME}?access_token=${MAPBOX_API_TOKEN}"

# TEST IF VALID RECIPE
# curl -X PUT "https://api.mapbox.com/tilesets/v1/validateRecipe?access_token=${MAPBOX_API_TOKEN}" \
#  -d @${JSON_RECIPE_FILEPATH} \
#  --header "Content-Type:application/json"

# SET TILESET JOB SPECS (GEOJSON SOURCE ID AND JSON RECIPE)
curl -X POST "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}?access_token=${MAPBOX_API_TOKEN}" \
 -d @${JSON_RECIPE_FILEPATH} \
 --header "Content-Type:application/json"

# SUBMIT TILESET JOB
curl -X POST "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}/publish?access_token=${MAPBOX_API_TOKEN}"

# RETRIEVE TILESET JOB STATUS
curl "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}/status?access_token=${MAPBOX_API_TOKEN}"

# IF SUCCESSFUL THE TILESET SHOULD BE AVAILABLE IN MAPBOX STUDIO ACCOUNT
