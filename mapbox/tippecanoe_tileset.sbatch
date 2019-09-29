#!/bin/bash

#SBATCH --job-name=tippecanoe_run
#SBATCH --partition=broadwl
#SBATCH --ntasks-per-node=1
#SBATCH --mem=56000
#SBATCH --output=logs/tippecanoe_run.out
#SBATCH --error=logs/tippecanoe_run.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=2:00:00
#SBATCH --account=rcc-staff

module load intel/18.0
module load gdal/2.4.1 
module load Anaconda3/5.1.0

# How to activate tippecanoe (do when running)
source activate mapbox

# Set destination directory
cd /project2/bettencourt/mnp/prclz/data/tilesets

# Convert GeoJSON to mbtiles
bash /project2/bettencourt/mnp/prclz/mapbox/tippecanoe_tileset.sh
