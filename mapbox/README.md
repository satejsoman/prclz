
## [Mapbox API Upload](https://docs.mapbox.com/api/maps/#tilesets) ##

### Preparing the files for upload  ###
* Set `TILESET_NAME=(<filename>)`
* Run `bash /project2/bettencourt/mnp/prclz/mapbox/cat_convert.sh` *warning: combines all CSVs files in complexity directory and converts to GeoJSON*

 ### Method 1: Tileset API (cloud mbtile processing) ###
 * Set the following parameters for file uploads to Mapbox (generate token [here](https://account.mapbox.com/access-tokens/create) and enable secret scopes):
    ```
    MAPBOX_API_TOKEN=()
    MAPBOX_USERNAME=(nmarchi0)
    TILESET_NAME=(Africa)
    COMPLEXITY_GEOJSON_FILEPATH=(/project2/bettencourt/mnp/prclz/data/tilesets/Africa.geojson)
    JSON_RECIPE_TEMPLATE=(/project2/bettencourt/mnp/prclz/mapbox/zoom_all_recipe.json)
    ```
 * Run `bash /project2/bettencourt/mnp/prclz/mapbox/tileset_api.sh` to upload GEOJSON to Mapbox
 
 ### Method 2: tippecanoe (local mbtile processing) ###
 * Use the [tippencanoe package](https://github.com/mapbox/tippecanoe) and build from source repo:
   ```
   conda install -c conda-forge tippecanoe
   source activate tippecanoe
   ```
 * Set `cd /project2/bettencourt/mnp/prclz/data/tilesets`, define `COMPLEXITY_GEOJSON_FILEPATH=()`, and run `bash /project2/bettencourt/mnp/prclz/mapbox/tippecanoe_tileset.sh`
 * Upload mbtiles through the UI [here](https://studio.mapbox.com/tilesets/)
 * Upload larger mbtiles via the S3 workflow [here](https://docs.mapbox.com/api/maps/#retrieve-s3-credentials)
 
  ### Basics of Mapbox Studio ###
  * Verify that uploaded tileset is available [here](https://studio.mapbox.com/tilesets/)
  * Go to https://studio.mapbox.com/ and select style for map
  * Go to "Select data" > "Data sources" > click uploaded tileset layer 
  * Go to "Style" > "Style across data range" > "Choose numeric data field": Complexity # Numeric
  * Edit color range (i.e., when complexity = 0 is green, complexity = 2 is white, complexity 20 = red)
  * Publish
 
