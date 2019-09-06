#!/bin/bash

#SBATCH --job-name=PARCELS_HTI
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=56000
#SBATCH --output=logs/parcels_HTI.out
#SBATCH --error=logs/parcels_HTI.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=36:00:00
#SBATCH --account=pi-bettencourt


building_list=()
for i in data/buildings/Central-America/HTI/*.geojson; do
    building_list+=("$i")
done
echo "${building_list[@]}"

set -e

for building in "${building_list[@]}"; do
    Rscript prclz/parcelization/midway_parcelization.R --building ${building};
done
