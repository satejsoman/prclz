#!/bin/bash

#SBATCH --job-name=csv_to_geojson
#SBATCH --partition=broadwl
#SBATCH --ntasks-per-node=1
#SBATCH --mem=56000
#SBATCH --output=logs/csv_to_geojson.out
#SBATCH --error=logs/csv_to_geojson.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=5:00:00
#SBATCH --account=rcc-staff

module load udunits/2.2
module load gdal/2.4.1 

cd /project2/bettencourt/mnp/prclz/data/tilesets

# rm global_file_2.geojson
# rm global_file_2.geojson.ld

# ogr2ogr -f "GeoJSON" global_file_2.geojson -dialect sqlite -sql "SELECT block_id, cast(complexity as integer) as complexity, GeomFromText(geometry) FROM global_file" global_file.csv -a_srs "WGS84"

ogr2ogr -f "GeoJSONSeq" global_file_2.geojson.ld global_file.geojson
