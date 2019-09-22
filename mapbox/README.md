## Mapbox How to Guide ##

#### Preparing the files for upload (combine CSVs and convert to GeoJSON and GeoJSON.ld)  ####
* The first step is to combine the GADM-level output from the k block complexity workflow and put in a Mapbox-friendly format
  ```
  # Update repo
  cd /project2/bettencourt/mnp/prclz
  git pull
  
  # Concatenate CSVs and convert to GeoJSON and GeoJSON.ld using ogr2ogr
  bash /project2/bettencourt/mnp/prclz/mapbox/csv_to_geojson.sh
  ``` 
* *(Warning: combines all CSVs files in this path `/project2/bettencourt/mnp/prclz/data/complexity/*/*/*.csv` and converts to one GeoJSON)*

### Mapbox API Upload ###

 #### Method 1: [Tileset API](https://docs.mapbox.com/api/maps/#tilesets) (cloud mbtile processing) ####
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
 
 #### Method 2: tippecanoe (local mbtile processing) ####
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
 * Upload mbtiles through the UI [here](https://studio.mapbox.com/tilesets/) (up to 25 GB mbtiles)

### Mapbox Styling ###

  #### Basics of Mapbox Studio ####
  * Verify that uploaded tileset is available [here](https://studio.mapbox.com/tilesets/)
  * Go to https://studio.mapbox.com/ and select style for map
  * Go to "Select data" > "Data sources" > click uploaded tileset layer 
  * Go to "Style" > "Style across data range" > "Choose numeric data field" > *Complexity # Numeric*
  * Edit color range (i.e., when complexity = 0 is green, complexity = 2 is white, complexity > 2 is red gradient)
  * Click "Share..." copy the "Your style URL" and the "Your access token"
  * Create a github.io account, create a repo, and commit changes and paste the access token and the style URL [in this HTML page](https://github.com/mansueto-institute/mansueto-institute.github.io/blob/master/_includes/mapbox.html) (also edit setView([longitude, latitude], zoom) and other stylings if needed)
      * [Simple map HTML template](https://docs.mapbox.com/mapbox-gl-js/example/simple-map/) and [initialize map with data](https://docs.mapbox.com/help/tutorials/mapbox-gl-js-expressions/#initialize-a-map-with-data)
  * Wait a minute and the map should populate the webpage here: https://mansueto-institute.github.io/
 
  #### Basics of Mapbox GL JS ####
  * Here is the link to the [404.html and index.html](https://github.com/mansueto-institute/prclz/tree/master/mapbox/build) and [Mapbox JS](https://github.com/mansueto-institute/raw-files/blob/master/mapbox/million_neighborhoods.js) that flow into the Mapbox visualization
  * Follow Mapbox examples for how to add [popups](https://docs.mapbox.com/mapbox-gl-js/example/popup-on-click/), [playback](https://docs.mapbox.com/mapbox-gl-js/example/playback-locations/), [style layers](https://docs.mapbox.com/mapbox-gl-js/example/setstyle/), or [choropleths](https://docs.mapbox.com/help/tutorials/choropleth-studio-gl-pt-2/)
  
### Deploying App ###

  #### How to Deploy the Map on Hosting Service ####
  * Add the TXT and A records from the hosting site to the DNS providers website
  * When your domain is connected to the hosting service you can deploy the single page HTML app
  * To deploy on Firebase [first setup an account](https://console.firebase.google.com/u/0/)
  * Install [node.js](https://nodejs.org/en/download/) and [nvm](https://github.com/nvm-sh/nvm) -- see [this site](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) for more info
  * Install the [Firebase CLI](https://firebase.google.com/docs/cli#install_the_firebase_cli) `npm install -g firebase-tools`
    * If you get an [error](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally) [follow this process](https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally) and run:
    ```
    # METHOD 1 -- must run each time you login to Firebase CLI
    alias firebase="`npm config get prefix`/bin/firebase"` 
    # METHOD 2 -- copy this into .bash_profile
    export PATH="<directory path from `npm get prefix`>/bin:$PATH"
    ```
  * To deploy the app run the following steps:
    ```
    cd ~/prclz/mapbox/build # this directory should contain the index.html file
    firebase login # connect local environment to cloud account
    firebase init # initializes in the above current directory
    
    # Firebase delivers a couple prompts:
    ? Which Firebase CLI features do you want to set up for this folder? Press Space to select features, then Enter to confirm your choices.
    >> Hosting: Configure and deploy Firebase Hosting sites
    ? What do you want to use as your public directory? 
    >> Delete (public) default and press return so that it works from existing directory 
    ? Configure as a single-page app (rewrite all urls to /index.html)? 
    >> No
    ? File /404.html already exists. Overwrite? 
    >> No
    ? File /index.html already exists. Overwrite? 
    >> No
    # adds firebase.json to the currect directory
    
    firebase deploy # pushes app to the domains that were linked to the hosting site
    firebase logout
    ```
