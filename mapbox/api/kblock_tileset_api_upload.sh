#!/bin/bash

MAPBOX_API_TOKEN=(::MAPBOX_API_TOKEN::)
MAPBOX_USERNAME=(nmarchi0)
JSON_RECIPE_TEMPLATE=(/project2/bettencourt/mnp/prclz/mapbox/api/zoom_all_recipe.json)
INPUT_ARRAY=(africa_file.geojson.ld asia_eur_oceania_file.geojson.ld latam_file.geojson.ld)

for f in ${INPUT_ARRAY[@]}; do
  TILESET_NAME=("${f%%.*}"_$(date '+%Y%m%d'))
  INPUT_GEOJSON=(/project2/bettencourt/mnp/prclz/data/tilesets/"${f}")
  echo "Processing $TILESET_NAME from $INPUT_GEOJSON"

  # FILL IN JSON RECIPE TEMPLATE
  JSON_RECIPE_FILEPATH=(/project2/bettencourt/mnp/prclz/data/tilesets/mapbox_recipe.json)
  sed -e "s/::MAPBOX_USERNAME::/${MAPBOX_USERNAME}/g" -e "s/::TILESET_NAME::/${TILESET_NAME}/g" < ${JSON_RECIPE_TEMPLATE} > ${JSON_RECIPE_FILEPATH}

  # UPLOAD AND CREATE GEOJSON SOURCE ID
  curl -F file=@${INPUT_GEOJSON} \
    "https://api.mapbox.com/tilesets/v1/sources/${MAPBOX_USERNAME}/${TILESET_NAME}?access_token=${MAPBOX_API_TOKEN}"

  # SET TILESET JOB SPECS (GEOJSON SOURCE ID AND JSON RECIPE)
  curl -X POST "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}?access_token=${MAPBOX_API_TOKEN}" \
    -d @${JSON_RECIPE_FILEPATH} \
    --header "Content-Type:application/json"

  # SUBMIT TILESET JOB
  curl -X POST "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}/publish?access_token=${MAPBOX_API_TOKEN}"

  # RETRIEVE TILESET JOB STATUS
  curl "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${TILESET_NAME}/status?access_token=${MAPBOX_API_TOKEN}"

done
