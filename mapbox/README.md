
## [Mapbox API Upload](https://docs.mapbox.com/api/maps/#tilesets) ##

* Set `cd /project2/bettencourt/mnp/prclz`
* Run `bash mapbox/cat_complexity.sh` to concatenate CSVs and write to `prclz/data/tilesets/`
* Run:
    ```
    module load intel/18.0
    module load gdal/2.2
    module load Anaconda3/5.1.0
    ```
    `python mapbox/csv_to_geojson.py prclz/data/tilesets/<filename.csv>` to write GEOJSONs to `prclz/data/tilesets/`
* Set the following parameters for file uploads to Mapbox:
    ```
    MAPBOX_API_TOKEN=()
    MAPBOX_USERNAME=(nmarchi0)
    TILESET_NAME=(Africa)
    COMPLEXITY_GEOJSON_FILEPATH=(/project2/bettencourt/mnp/prclz/data/tilesets/Africa.geojson)
    JSON_RECIPE_FILEPATH=(/project2/bettencourt/mnp/prclz/mapbox/recipe_wo_toplevel.json)
    ```
 * Run `bash mapbox/tileset_api.sh` to upload GEOJSON to Mapbox
 
 
 * If all else fails use the [tippencanoe package](https://github.com/mapbox/tippecanoe):
    * Build from source repo:
        ```
        conda activate mnp
        conda install -c conda-forge tippecanoe
        ```
    * Run `base prclz/mapbox/tippecanoe_tileset.sh prclz/data/tilesets/<filename.geojson>`
