#!/bin/bash

set -e 

for countrycode in $(ls data/blocks/Africa/); do 
countryname=$(grep "$countrycode" midway/country_codes.csv | rev | cut -d, -f2 | rev)
mkdir -p data/complexity/Africa/${countrycode}
echo "$countryname ($countrycode)"
< midway/parallel_complexity_template.sbatch sed -e "s/::COUNTRYCODE::/${countrycode}/g" -e "s/::COUNTRYNAME::/${countryname}/g" > midway/filled_templates/${countrycode}_complexity.sbatch 
sbatch midway/filled_templates/${countrycode}_complexity.sbatch 
done
