
# Concatenate CSVs
head -1 /project2/bettencourt/mnp/prclz/mapbox/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/global_file.csv
find /project2/bettencourt/mnp/prclz/data/complexity/*/*/*.csv -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/global_file.csv 
    echo "$file"
done

# Convert CSV to GeoJSON
ogr2ogr -f "GeoJSON" /project2/bettencourt/mnp/prclz/data/tilesets/global_file.geojson /project2/bettencourt/mnp/prclz/data/tilesets/global_file.csv 
