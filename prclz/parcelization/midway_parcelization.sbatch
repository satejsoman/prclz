#!/bin/bash

#SBATCH --job-name=PARCELS_::COUNTRYCODE::
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks=24
#SBATCH --output=logs/parcels_::COUNTRYCODE::.out
#SBATCH --error=logs/parcels_::COUNTRYCODE::.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=2:00:00
#SBATCH --account=pi-bettencourt

module load R/3.5.1

set -e
for building in data/geojson_gadm/Africa/::COUNTRYCODE::/*.geojson; do
    Rscript midway/midway_parcelization.R --building ${building};
done

