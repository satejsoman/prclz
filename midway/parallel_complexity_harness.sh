#!/bin/bash

set -e 
template="#!/bin/bash
#SBATCH --job-name=k_::COUNTRYCODE::
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --mem=20G
#SBATCH --ntasks=24
#SBATCH --output=logs/k_::COUNTRYCODE::.out
#SBATCH --error=logs/k_::COUNTRYCODE::.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=satej@uchicago.edu
#SBATCH --time=36:00:00
#SBATCH --account=pi-bettencourt
set -e

mkdir -p data/complexity/::CONTINENT::/::COUNTRYNAME::

for block in data/blocks/Africa/::COUNTRYCODE::/*.csv; do
    python midway/midway_complexity.py --blocks \$block --buildings data/geojson/::CONTINENT::/::COUNTRYNAME::_buildings.geojson --output \${block//blocks/complexity} --parallelism 24;
done"

grep "HTI\|NPL\|SLE\|LBR" data_processing/country_codes.csv | rev | cut -d, -f2,3,4 | rev | tr , ' ' | while read country_code country_name continent; do
    continent=$(python -c "print('${continent}'.split('/')[0].title())")
    echo "${template}" | sed -e "s/::COUNTRYCODE::/${country_code}/g" -e "s/::COUNTRYNAME::/${country_name}/g" -e "s'::CONTINENT::'${continent}'g "> midway/filled_templates/k_${country_code}.sbatch
    echo "$(sbatch midway/filled_templates/k_${country_code}.sbatch) (${country_code}/${country_name})"
done
