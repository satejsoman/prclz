#!/bin/bash

template="#!/bin/bash
#SBATCH --job-name=blocks_::COUNTRYCODE::
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks=24
#SBATCH --output=logs/blocks_::COUNTRYCODE::.out
#SBATCH --error=logs/blocks_::COUNTRYCODE::.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=satej@uchicago.edu
#SBATCH --time=36:00:00
#SBATCH --account=pi-bettencourt
set -e

mkdir -p data/blocks/::CONTINENT::/::COUNTRYCODE::

python midway/midway_blocks.py --gadm ::GADM:: --linestrings data/geojson/::CONTINENT::/::COUNTRYNAME::_lines.geojson --output data/blocks/::CONTINENT::/::COUNTRYCODE:: --parallelism 24" 

# iterate over the countries listed
grep -v africa data_processing/country_codes.csv | tail -n +2 | rev | cut -d, -f2,3,4 | rev | tr , ' ' | while read country_code country_name continent; do 
# grep -v africa data_processing/country_codes_pr_onwards.csv | rev | cut -d, -f2,3,4 | rev | tr , ' ' | while read country_code country_name continent; do 
  if [ ! -z "${continent}" ]; then
    # map the country codes entry to the continent folder
    continent=$(python -c "print('${continent}'.split('/')[0].title())")

    # figure out the appropriate GADM level
    gadm=$(ls data/GADM/${country_code}/*.shp | python -c "import sys; print(sorted(sys.stdin.readlines())[-1].strip())")

    # log it
    echo "${country_code} ${country_name} ${continent} ${gadm}"

    # fill in the template for the sbatch 
    echo "${template}" | sed -e "s'::GADM::'${gadm}'g" -e "s/::COUNTRYCODE::/${country_code}/g" -e "s/::COUNTRYNAME::/${country_name}/g" -e "s'::CONTINENT::'${continent}'g "> midway/filled_templates/blocks_${country_code}.sbatch
    echo "submitting job"
    sbatch midway/filled_templates/blocks_${country_code}.sbatch
    sleep 2
  else 
    echo "no country code found for ${country_code} ${country_name}"
  fi 
echo
done

