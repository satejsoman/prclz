#!/bin/bash

template="#!/bin/bash
#SBATCH --job-name=k_::COUNTRYCODE::
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks=28
#SBATCH --mem=45G
#SBATCH --output=logs/k_::COUNTRYCODE::.out
#SBATCH --error=logs/k_::COUNTRYCODE::.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=36:00:00
#SBATCH --account=pi-bettencourt
set -euo pipefail

mkdir -p data/complexity/::CONTINENT::/::COUNTRYCODE::

source activate mnp
module load parallel

ulimit -u 10000

echo \" number of building files           : \$(ls data/buildings/::CONTINENT::/::COUNTRYCODE::/  | wc -l) \"
echo \" number of existing complexity files: \$(ls data/complexity/::CONTINENT::/::COUNTRYCODE::/ | wc -l) \"

find data/buildings/::CONTINENT::/::COUNTRYCODE::/buildings*.geojson | 
xargs -I% bash -c 'building=%; echo \$(echo \${building//buildings/blocks} | sed -e \"s/geojson/csv/g\") \$building \$(echo \${building//buildings/complexity} | sed -e \"s/geojson/csv/g\")' |
parallel --colsep='\ ' --delay 0.2 -j \$SLURM_NTASKS --joblog logs/parallel_k_::COUNTRYCODE::.log --resume -I{} \"srun --exclusive -N1 -n1 python midway/single_file_complexity.py --blocks {1} --buildings {2} --output {3} \""

filter="BFA\|CMR\|TCD\|COD\|GIN\|LSO\|MWI\|MLI\|MAR\|MOZ\|NPL\|NGA\|SLE\|SSD\|TZA\|ZMB"

grep "${filter}" data_processing/country_codes.csv | 
rev | cut -d, -f2,3,4 | rev | tr , ' ' | 
while read country_code country_name continent; do
    continent=$(python -c "print('${continent}'.split('/')[0].title())")
    echo -n "${country_code} ${country_name} ${continent} | "
    echo "${template}" | sed -e "s/::COUNTRYCODE::/${country_code}/g" -e "s/::COUNTRYNAME::/${country_name}/g" -e "s'::CONTINENT::'${continent}'g" > midway/filled_templates/k_${country_code}.sbatch
    sbatch midway/filled_templates/k_${country_code}.sbatch
done | column -t 
