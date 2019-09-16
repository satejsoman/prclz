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

bash /project2/bettencourt/mnp/prclz/mapbox/tippecanoe_tileset.sh
