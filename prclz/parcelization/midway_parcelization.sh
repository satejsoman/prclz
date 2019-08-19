#!/bin/bash

set -e

for countrycode in $(ls data/geojson_gadm/Africa/); do
countryname=$(grep "$countrycode" midway/country_codes.geojson | rev | cut -d, -f2 | rev)
mkdir -p data/parcels/Africa/${countrycode}
echo "$countryname ($countrycode)"
< midway/midway_parcelization.sbatch sed -e "s/::COUNTRYCODE::/${countrycode}/g" -e "s/::COUNTRYNAME::/${countryname}/g" > midway/filled_templates/${countrycode}_parcels.sbatch
sbatch midway/filled_templates/${countrycode}_parcels.sbatch
done
