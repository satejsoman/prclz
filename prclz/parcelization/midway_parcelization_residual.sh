#!/bin/bash

set -e

module load R/3.6.1
module load udunits/2.2
module load gdal/2.4.1 

# Create output directories that mirror input directories
for i in data/buildings/*/*; do
    j=("${i//buildings/parcels}")
    mkdir -p "$j"
    echo "$j"
done

# Add input files to array
parcel_list=()
for i in data/parcels/*/*/*.geojson; do
    parcel_list+=("$i")
done
parcel_list=("${parcel_list[@]//parcels/buildings}")
#echo "${parcel_list[@]}"

# Add output files to array
building_list=()
for i in data/buildings/*/*/*.geojson; do
    building_list+=("$i")
done
#echo "${building_list[@]}"

# List residual between output and input files
residual_list=()
residual_list=(`echo ${building_list[@]} ${parcel_list[@]} | tr ' ' '\n' | sort | uniq -u`)

# List countries with residual input files
country_list=()
country_list=(`echo ${residual_list[@]} | tr ' ' '\n' | sort | cut -d'/' -f 4 | uniq`)
printf '%s\n' "${country_list[@]}"

country_list=(NPL)

# Submit a job for each residual country
for countrycode in ${country_list[@]}; do
echo "$countrycode"
< prclz/parcelization/midway_parcelization_residual.sbatch sed -e "s/::COUNTRYCODE::/${countrycode}/g" > prclz/parcelization/filled_templates/${countrycode}_parcels.sbatch
sbatch prclz/parcelization/filled_templates/${countrycode}_parcels.sbatch
done

