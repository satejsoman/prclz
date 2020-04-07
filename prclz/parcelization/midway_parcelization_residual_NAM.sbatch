#!/bin/bash

#SBATCH --job-name=parcels_NAM
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=56000
#SBATCH --output=logs/parcels_NAM.out
#SBATCH --error=logs/parcels_NAM.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cnederhood@uchicago.edu
#SBATCH --time=6:00:00
#SBATCH --account=pi-bettencourt

# If output file exists in parcels directory add to array
parcel_list=()
for i in data/dg_parcels/*/NAM/*.geojson; do
    [ -f "$i" ] || continue
    parcel_list+=("$i")
done
parcel_list=("${parcel_list[@]//parcels/buildings}")
#echo "${parcel_list[@]}"

# If input file exists in buildings directory add to array
building_list=()
for i in data/dg_buildings/*/NAM/*.geojson; do
    [ -f "$i" ] || continue
    building_list+=("$i")
done
#echo "${building_list[@]}"

# Find residual building input files with no corresponding parcel output files
residual_list=()
residual_list=(`echo ${building_list[@]} ${parcel_list[@]} | tr ' ' '\n' | sort | uniq -u `)
#echo "${residual_list[@]}"

printf '%s\n' "${residual_list[@]}"

set -e

# Execute script on residual building input files
for building in "${residual_list[@]}"; do
    Rscript prclz/parcelization/midway_parcelization_digital_globe.R --building ${building};
done
