
## Mapbox API Upload ##

### Preparing the files for upload (combine CSVs and convert to GeoJSON and GeoJSON.ld)  ###
* The first step is to combine the GADM-level output from the k block complexity workflow and put in a Mapbox-friendly format
  ```
  # Update repo
  cd /project2/bettencourt/mnp/prclz
  git pull
  
  # Concatenate CSVs and convert to GeoJSON and GeoJSON.ld using ogr2ogr
  bash /project2/bettencourt/mnp/prclz/mapbox/csv_to_geojson.sh
  ``` 
* *(Warning: combines all CSVs files in this path `/project2/bettencourt/mnp/prclz/data/complexity/*/*/*.csv` and converts to one GeoJSON)*

 ### Method 1: [Tileset API](https://docs.mapbox.com/api/maps/#tilesets) (cloud mbtile processing) ###
 * Generate Mapbox token [here](https://account.mapbox.com/access-tokens/create) and enable secret scopes
    ```
    MAPBOX_API_TOKEN=(<INSERT TOKEN HERE>)
    ```
 * Check parameter defaults in [tileset_api.sh](https://github.com/mansueto-institute/prclz/blob/master/mapbox/tileset_api.sh) and change as needed.
    ```
    sed -e "s/::MAPBOX_API_TOKEN::/${MAPBOX_API_TOKEN}/g" < /project2/bettencourt/mnp/prclz/mapbox/tileset_api.sh > /project2/bettencourt/mnp/prclz/mapbox/tileset_api_filled.sh
    ```
 * Then run the API calls `bash /project2/bettencourt/mnp/prclz/mapbox/tileset_api_filled.sh` to upload GEOJSON.ld to Mapbox
 * A [Tileset CLI](https://github.com/mapbox/tilesets-cli/) is also available which is a wrapper for the Tileset API 
 
 ### Method 2: tippecanoe (local mbtile processing) ###
 * Use the [tippencanoe package](https://github.com/mapbox/tippecanoe) and build from conda forge:
   ```
   # How to install tippecanoe (only do once)
   module load intel/18.0
   module load gdal/2.4.1 
   module unload python
   module load Anaconda3/5.1.0
   conda create --name mapbox # only do this once
   conda install -n mapbox tippecanoe
   
   # How to activate tippecanoe (do when running)
   source activate mapbox
   ```
 * Convert GeoJSON files to mbtiles
   ```
   cd /project2/bettencourt/mnp/prclz/data/tilesets
   sbatch /project2/bettencourt/mnp/prclz/mapbox/tippecanoe_tileset.sbatch
   ```
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
      * [Simple map HTML template](https://docs.mapbox.com/mapbox-gl-js/example/simple-map/) and [initialize map with data](https://docs.mapbox.com/help/tutorials/mapbox-gl-js-expressions/#initialize-a-map-with-data)
  * Wait a minute and the map should populate the webpage here: https://mansueto-institute.github.io/
 
  ### Basics of Mapbox GL JS ###
