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

# Convert CSV to GeoJSON
module load udunits/2.2
module load gdal/2.4.1 

cd /project2/bettencourt/mnp/prclz/data/tilesets

rm africa_file.geojson.ld

# Convert CSV to GeoJSON-line delimited
ogr2ogr -f "GeoJSONSeq" africa_file.geojson.ld -dialect sqlite -sql "SELECT block_id, cast(complexity as integer) as complexity, GeomFromText(geometry) FROM africa_file" africa_file.csv -a_srs "WGS84"
