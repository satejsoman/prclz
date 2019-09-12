
## Mapbox ETL ##

* Run `bash prclz/mapbox/cat_complexity.sh` to concatenate CSVs together and output to this directory `/project2/bettencourt/mnp/prclz/data/tilesets/`
* Run `python prclz/mapbox/csv_to_geojson.py <filename.csv>` to convert to GEOJSON to this directory `/project2/bettencourt/mnp/prclz/data/tilesets/`
* Set the following parameters for file uploads to Mapbox:
    ```
    MAPBOX_API_TOKEN=()
    MAPBOX_USERNAME=(nmarchi0)
    TILESET_NAME=(Africa)
    COMPLEXITY_GEOJSON_FILEPATH=(/project2/bettencourt/mnp/prclz/data/tilesets/Africa.geojson)
    JSON_RECIPE_FILEPATH=(prclz/mapbox/recipe_wo_toplevel.json)
    ```
 * Run `bash prclz/mapbox/tileset_api.sh` to upload GEOJSON to Mapbox



## Archive ##

* `tippencanoe` [package](https://github.com/mapbox/tippecanoe)
* [How to access OSM building via Mapbox](https://github.com/mapbox/malaria-mapping)
* [Mapbox API upload docs](https://docs.mapbox.com/api/maps/#datasets)


### Build tippecanoe from the source repository ###
```
conda activate mnp
conda install -c conda-forge tippecanoe
```

### Set current directory ###
`cd /project2/bettencourt/mnp/prclz`

### Make directory ###
`mkdir /project2/bettencourt/mnp/prclz/data/mapbox`
