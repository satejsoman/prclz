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

parcel_list=()
for i in $(ls data/parcels/*/HTI/); do
    parcel_list+=("$i")
done
parcel_list=("${parcel_list[@]//parcels/buildings}")
echo "${parcel_list[@]}"

building_list=()
for i in data/buildings/*/HTI/*.geojson; do
    building_list+=("$i")
done
echo "${building_list[@]}"

residual_list=()
residual_list=(`echo ${building_list[@]} ${parcel_list[@]} | tr ' ' '\n' | sort | uniq -u `)
echo "${residual_list[@]}"

printf '%s\n' "${residual_list[@]}"

set -e

for building in "${residual_list[@]}"; do
    Rscript prclz/parcelization/midway_parcelization.R --building ${building};
done
