
## Mapbox API Upload ##

### Preparing the files for upload (combine CSVs and convert to GeoJSON.ld)  ###
* Run `cd /project2/bettencourt/mnp/prclz` and `git pull`
* Load modules and activate environment
  ``` 
  module load intel/18.0
  module load gdal/2.4.1 
  source activate mnp
  ```
* Run `bash /project2/bettencourt/mnp/prclz/mapbox/cat_convert.sh` 
  *(Warning: combines all CSVs files in this path `/project2/bettencourt/mnp/prclz/data/complexity/*/*/*.csv` and converts to one GeoJSON)*

 ### Method 1: [Tileset API](https://docs.mapbox.com/api/maps/#tilesets) (cloud mbtile processing) ###
 * Generate Mapbox token [here](https://account.mapbox.com/access-tokens/create) and enable secret scopes
    ```
    MAPBOX_API_TOKEN=(<INSERT TOKEN HERE>)
    ```
 * Check parameter defaults in [tileset_api.sh](https://github.com/mansueto-institute/prclz/blob/master/mapbox/tileset_api.sh) and change as needed.
    ```
    sed -e "s/::MAPBOX_API_TOKEN::/${MAPBOX_API_TOKEN}/g" < /project2/bettencourt/mnp/prclz/mapbox/tileset_api.sh > /project2/bettencourt/mnp/prclz/mapbox/tileset_api_filled.sh
    ```
 * Then run the API calls
    ```
    # SET PARAMETERS
    MAPBOX_API_TOKEN=(::MAPBOX_API_TOKEN::)
    MAPBOX_USERNAME=(nmarchi0)
    TILESET_NAME=(global_file_$(date '+%Y%m%d'))
    COMPLEXITY_GEOJSON_FILEPATH=(/project2/bettencourt/mnp/prclz/data/tilesets/global_file.geojson)
    JSON_RECIPE_TEMPLATE=(/project2/bettencourt/mnp/prclz/mapbox/zoom_all_recipe.json)

    # FILL IN JSON RECIPE TEMPLATE
    JSON_RECIPE_FILEPATH=(/project2/bettencourt/mnp/prclz/data/tilesets/mapbox_recipe.json)
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
    ```
 * The one liner bash version is: `bash /project2/bettencourt/mnp/prclz/mapbox/tileset_api_filled.sh` to upload GEOJSON.ld to Mapbox
 
 ### Method 2: tippecanoe (local mbtile processing) ###
 * Use the [tippencanoe package](https://github.com/mapbox/tippecanoe) and build from conda forge:
   ```
   module load intel/18.0
   module load gdal/2.4.1 
   module unload python
   module load Anaconda3/5.1.0
   conda install -c conda-forge tippecanoe
   source activate tippecanoe
   ```
 * Set destination directory `cd /project2/bettencourt/mnp/prclz/data/tilesets`
 * Run `bash /project2/bettencourt/mnp/prclz/mapbox/tippecanoe_tileset.sh`
 * Upload mbtiles through the UI [here](https://studio.mapbox.com/tilesets/)
 * Upload larger mbtiles via the S3 workflow [here](https://docs.mapbox.com/api/maps/#retrieve-s3-credentials)
 
  ### Basics of Mapbox Studio ###
  * Verify that uploaded tileset is available [here](https://studio.mapbox.com/tilesets/)
  * Go to https://studio.mapbox.com/ and select style for map
  * Go to "Select data" > "Data sources" > click uploaded tileset layer 
  * Go to "Style" > "Style across data range" > "Choose numeric data field" > *Complexity # Numeric*
  * Edit color range (i.e., when complexity = 0 is green, complexity = 2 is white, complexity > 2 is red gradient)
  * Click "Share..." copy the "Your style URL" and the "Your access token"
  * Create a github.io account, create a repo, and commit changes and paste the access token and the style URL [in this HTML page](https://github.com/mansueto-institute/mansueto-institute.github.io/blob/master/_includes/mapbox.html) (also edit setView([longitude, latitude], zoom) and other stylings if needed)
  * Wait a minute and the map should populate the webpage here: https://mansueto-institute.github.io/
 
