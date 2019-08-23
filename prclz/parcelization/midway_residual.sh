
parcel_list=()
for i in data/parcels/Africa/*/*.geojson; do
    parcel_list+=("$i")
done
parcel_list=("${parcel_list[@]/parcels/geojson_gadm}")
parcel_list=("${parcel_list[@]/parcels/buildings}")
echo "${parcel_list[@]}"

building_list=()
for i in data/geojson_gadm/Africa/*/*.geojson; do
    building_list+=("$i")
done
echo "${building_list[@]}"

residual_list=()
residual_list=(`echo ${building_list[@]} ${parcel_list[@]} | tr ' ' '\n' | sort | uniq -u `)
echo "${residual_list[@]}"

printf '%s\n' "${residual_list[@]}"

#!/bin/bash

#SBATCH --job-name=PARCELS_::COUNTRYCODE::
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=64000
#SBATCH --output=logs/parcels_::COUNTRYCODE::.out
#SBATCH --error=logs/parcels_::COUNTRYCODE::.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=8:00:00
#SBATCH --account=pi-bettencourt

set -e

for building in "${residual_list[@]}"; do
    Rscript prclz/parcelization/midway_parcelization.R --building ${building};
done
