#!/bin/bash

# Concatenate CSVs
head -1 /project2/bettencourt/mnp/prclz/mapbox/api/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/global_file.csv
find /project2/bettencourt/mnp/prclz/data/complexity/*/*/ -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/global_file.csv 
    echo "$file"
done

# Convert CSV to GeoJSON using R
# module load R/3.6.1
module load udunits/2.2
module load gdal/2.4.1 
# Rscript /project2/bettencourt/mnp/prclz/mapbox/csv_to_geojson.R 

cd /project2/bettencourt/mnp/prclz/data/tilesets

rm  global_file.geojson
rm global_file.geojson.ld

# Convert CSV to GeoJSON
ogr2ogr -f "GeoJSON" global_file.geojson -dialect sqlite -sql "SELECT block_id, cast(complexity as integer) as complexity, GeomFromText(geometry) FROM global_file" global_file.csv -a_srs "WGS84"

# Convert GeoJSON to GeoJSON-line delimited
ogr2ogr -f "GeoJSONSeq" global_file.geojson.ld global_file.geojson
