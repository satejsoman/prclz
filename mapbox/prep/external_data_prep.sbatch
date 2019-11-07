#!/bin/bash

#SBATCH --job-name=external_data_prep
#SBATCH --partition=broadwl
#SBATCH --ntasks=1
#SBATCH --mem=56000
#SBATCH --output=logs/external_data_prep.out
#SBATCH --error=logs/external_data_prep.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=8:00:00
#SBATCH --account=rcc-staff

set -e

module load udunits/2.2
module load gdal/2.4.1

continent_list=(Africa  Asia  Australia-Oceania  Central-America  Europe  North-America  South-America)
printf '%s\n' "${continent_list[@]}"

for i in "${continent_list[@]}"; do
  echo "$i"
  mkdir -p /project2/bettencourt/mnp/prclz/data/data_release/"$i"
  country_list=($(ls /project2/bettencourt/mnp/prclz/data/complexity/"$i"))
  for j in "${country_list[@]}"; do
    echo "$j"
    head -1 /project2/bettencourt/mnp/prclz/mapbox/api/header.csv > /project2/bettencourt/mnp/prclz/data/data_release/"$i"/"$j".csv
    find /project2/bettencourt/mnp/prclz/data/complexity/"$i"/"$j" -name "*.csv" | while read file
    do
      tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/data_release/"$i"/"$j".csv
      echo "$file"
    done
    sql_string="SELECT block_id, cast(complexity as integer) as complexity, GeomFromText(geometry) FROM "
    sql_string+="$j"
    echo "$sql_string"
    ogr2ogr -f "GeoJSON" /project2/bettencourt/mnp/prclz/data/data_release/"$i"/"$j".geojson -dialect sqlite -sql "$sql_string" /project2/bettencourt/mnp/prclz/data/data_release/"$i"/"$j".csv -a_srs "WGS84"
  done
done
