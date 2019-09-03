#!/bin/bash

template="#!/bin/bash
#SBATCH --job-name=sfb_::COUNTRYCODE::
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH --output=logs/sfb_::COUNTRYCODE::.out
#SBATCH --error=logs/sfb_::COUNTRYCODE::.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=satej@uchicago.edu
#SBATCH --time=36:00:00
#SBATCH --account=pi-bettencourt
set -e

mkdir -p data/blocks/::CONTINENT::/::COUNTRYCODE::

module load parallel

ulimit -u 10000

find data/GADM_split/::COUNTRYCODE::/ -maxdepth 1 -type f | parallel --delay 0.2 -j \$SLURM_NTASKS --joblog runtask.log --resume -I{} \"srun --exclusive -N1 -n1 python midway/midway_blocks.py --gadm {} --linestrings data/geojson/::CONTINENT::/::COUNTRYNAME::_lines.geojson --output data/blocks/::CONTINENT::/::COUNTRYCODE::\""

grep "MEX\|CHN\|IRN\|IND\|MYS\|PHL\|THA\|IDN\|BRA" data_processing/country_codes.csv | rev | cut -d, -f2,3,4 | rev | tr , ' ' | while read country_code country_name continent; do
    echo "${template}" | sed -e "s/::COUNTRYCODE::/${country_code}/g" -e "s/::COUNTRYNAME::/${country_name}/g" -e "s'::CONTINENT::'${continent}'g "> midway/filled_templates/sfb_${country_code}.sbatch
    echo "$(sbatch midway/filled_templates/sfb_${country_code}.sbatch) (${country_code})"
done