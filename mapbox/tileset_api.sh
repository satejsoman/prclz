
MAPBOX_API_TOKEN=()
MAPBOX_USERNAME=(nmarchi0)
TILESET_NAME=(tile_test)
COMPLEXITY_GEOJSON_FILEPATH=()
JSON_RECIPE_FILEPATH=()

# DELETE TILESET SOURCE ID (TO OVERWRITE EXISTING TILESET)
curl -X DELETE "https://api.mapbox.com/tilesets/v1/sources/${MAPBOX_USERNAME}/${TILESET_NAME}?access_token=${MAPBOX_API_TOKEN}"

# UPLOAD AND CREATE GEOJSON SOURCE ID
curl -F file=@${COMPLEXITY_GEOJSON_FILEPATH} \
  "https://api.mapbox.com/tilesets/v1/sources/${MAPBOX_USERNAME}/${TILESET_NAME}?access_token=${MAPBOX_API_TOKEN}"

# TEST IF VALID RECIPE
curl -X PUT "https://api.mapbox.com/tilesets/v1/validateRecipe?access_token=${MAPBOX_API_TOKEN}" \
 -d @${JSON_RECIPE_FILEPATH} \
 --header "Content-Type:application/json"

# SET TILESET JOB SPECS (GEOJSON SOURCE ID AND JSON RECIPE)
curl -X POST "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}?access_token=${MAPBOX_API_TOKEN}" \
 -d @${JSON_RECIPE_FILEPATH} \
 --header "Content-Type:application/json"

# SUBMIT TILESET JOB
curl -X POST "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}/publish?access_token=${MAPBOX_API_TOKEN}"

# RETRIEVE TILESET JOB STATUS
curl "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}/status?access_token=${MAPBOX_API_TOKEN}"

# IF SUCCESSFUL THE TILESET SHOULD BE AVAILABLE IN MAPBOX STUDIO ACCOUNT
