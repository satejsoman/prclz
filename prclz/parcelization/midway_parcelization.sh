#!/bin/bash

set -e

module load R/3.6.1
module load udunits/2.2
module load gdal/2.4.1 

for countrycode in $(ls data/geojson_gadm/Africa/); do
countryname=$(grep "$countrycode" midway/country_codes.geojson | rev | cut -d, -f2 | rev)
mkdir -p data/parcels/Africa/${countrycode}
echo "$countryname ($countrycode)"
< midway/midway_parcelization.sbatch sed -e "s/::COUNTRYCODE::/${countrycode}/g" -e "s/::COUNTRYNAME::/${countryname}/g" > midway/filled_templates/${countrycode}_parcels.sbatch
sbatch midway/filled_templates/${countrycode}_parcels.sbatch
done
