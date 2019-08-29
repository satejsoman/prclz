#!/bin/bash

set -e

module load R/3.6.1
module load udunits/2.2
module load gdal/2.4.1 

for countrycode in $(ls data/buildings/Africa/); do
countryname=$(grep "$countrycode" data_processing/country_codes.csv | rev | cut -d, -f2 | rev)
mkdir -p data/parcels/Africa/${countrycode}
mkdir -p prclz/parcelization/filled_templates
echo "$countryname ($countrycode)"
< prclz/parcelization/midway_parcelization_residual.sbatch sed -e "s/::COUNTRYCODE::/${countrycode}/g" -e "s/::COUNTRYNAME::/${countryname}/g" > prclz/parcelization/filled_templates/${countrycode}_parcels.sbatch
sbatch prclz/parcelization/filled_templates/${countrycode}_parcels.sbatch
done

