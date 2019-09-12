
module load gdal/2.4.1 

# Concatenate CSVs
head -1 /project2/bettencourt/mnp/prclz/mapbox/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/${TILESET_NAME}.csv
find /project2/bettencourt/mnp/prclz/data/complexity/*/*/*.csv -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/${TILESET_NAME}.csv 
    echo "$file"
done

# Convert CSV to GeoJSON
ogr2ogr -f "GeoJSON" /project2/bettencourt/mnp/prclz/data/tilesets/${TILESET_NAME}.geojson /project2/bettencourt/mnp/prclz/data/tilesets/${TILESET_NAME}.csv 
