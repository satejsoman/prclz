#!/bin/bash

#SBATCH --job-name=csv_to_geojson
#SBATCH --partition=broadwl
#SBATCH --ntasks-per-node=1
#SBATCH --mem=56000
#SBATCH --output=logs/csv_to_geojson.out
#SBATCH --error=logs/csv_to_geojson.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=8:00:00
#SBATCH --account=rcc-staff

module load udunits/2.2
module load gdal/2.4.1 

cd /project2/bettencourt/mnp/prclz/data/tilesets

# Africa
head -1 /project2/bettencourt/mnp/prclz/mapbox/api/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/africa_file.csv 
find /project2/bettencourt/mnp/prclz/data/complexity/Africa/*/ -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/africa_file.csv 
    echo "$file"
done

# Asia, Europe, Oceania
head -1 /project2/bettencourt/mnp/prclz/mapbox/api/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/asia_eur_oceania_file.csv 
find /project2/bettencourt/mnp/prclz/data/complexity/ \( -type f -and -path '*/Asia/*' -or -path '*/Australia-Oceania/*' -or -path '*/Europe/*' \) -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/asia_eur_oceania_file.csv 
    echo "$file"
done

# Latin America
head -1 /project2/bettencourt/mnp/prclz/mapbox/api/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/latam_file.csv 
find /project2/bettencourt/mnp/prclz/data/complexity/ \( -type f -and -path '*/North-America/*' -or -path '*/Central-America/*' -or -path '*/South-America/*' \) -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/latam_file.csv 
    echo "$file"
done

# Convert CSV to GeoJSON
module load udunits/2.2
module load gdal/2.4.1 

cd /project2/bettencourt/mnp/prclz/data/tilesets

rm africa_file.geojson.ld
rm asiaeuraus_file.geojson.ld
rm latam_file.geojson.ld

# Convert CSV to GeoJSON-line delimited
ogr2ogr -f "GeoJSONSeq" africa_file.geojson.ld -dialect sqlite -sql "SELECT block_id, cast(complexity as integer) as complexity, GeomFromText(geometry) FROM africa_file" africa_file.csv -a_srs "WGS84"
ogr2ogr -f "GeoJSONSeq" asia_eur_oceania_file.geojson.ld -dialect sqlite -sql "SELECT block_id, cast(complexity as integer) as complexity, GeomFromText(geometry) FROM asia_eur_oceania_file" asia_eur_oceania_file.csv -a_srs "WGS84"
ogr2ogr -f "GeoJSONSeq" latam_file.geojson.ld -dialect sqlite -sql "SELECT block_id, cast(complexity as integer) as complexity, GeomFromText(geometry) FROM latam_file" latam_file.csv -a_srs "WGS84"

