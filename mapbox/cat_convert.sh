
# Concatenate CSVs
head -1 /project2/bettencourt/mnp/prclz/mapbox/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/global_file.csv
find /project2/bettencourt/mnp/prclz/data/complexity/*/*/*.csv -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/global_file.csv 
    echo "$file"
done

# Convert CSV to GeoJSON
module load R/3.6.1
module load udunits/2.2
module load gdal/2.4.1 
Rscript /project2/bettencourt/mnp/prclz/mapbox/csv_to_geojson.R 

# Convert GeoJSON to GeoJSON-line delimited
ogr2ogr -f GeoJSONSeq /project2/bettencourt/mnp/prclz/data/tilesets/global_file.geojson.ld /project2/bettencourt/mnp/prclz/data/tilesets/global_file.geojson
