#!/bin/bash

set -e

# module load R/3.6.1
# module load udunits/2.2
# module load gdal/2.4.1 

for countryfile in $(ls ../data/geojson/*/*buildings*); do
  file=$(echo $countryfile  | rev | cut -d/ -f1 | rev)
  countryname=${file/_buildings.geojson/}
  countryname=${countryname/_lines.geojson/}

  type=${file/${countryname}/}
  type=${type/_/}
  type=${type/.geojson/}

  if [[ ${countryname}=="guinea" ]]
  then 
  	countrycode="GIN"
  else
    countrycode=$(grep ${countryname} country_codes.csv | rev | cut -d, -f4 | rev)
  fi

  echo file=$file
  echo countryname=$countryname 
  echo type=$type
  echo countrycode=$countrycode
  echo 

  mkdir -p filled_templates
  cat midway_split_geojson.sbatch | sed -e "s/::TYPE::/${type}/g" -e "s/::COUNTRYCODE::/${countrycode}/g" -e "s/::FILEPATH::/${file}/g"> filled_templates/${countrycode}_${type}.sbatch
  #sbatch filled_templates/${countrycode}_parcels.sbatch
done
