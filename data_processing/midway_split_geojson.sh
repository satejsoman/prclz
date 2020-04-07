#!/bin/bash

set -e

# module load R/3.6.1
# module load udunits/2.2
# module load gdal/2.4.1 

ALL_COUNTRIES="country_list.txt"
type="buildings"     
REGION="africa"

while IFS= read -r countrycode
do
  countryname=$(grep "$countrycode" country_codes.csv | rev | cut -d, -f3 | rev)
  region=$(grep "$countrycode" country_codes.csv | rev | cut -d, -f2 | rev)
  file=${countryname}_${type}.geojson 

  if [[ ${region} == ${REGION} ]]
  then
      echo file=$file
      echo countryname=$countryname 
      echo region=$region 
      echo type=$type
      echo countrycode=$countrycode
      echo 

      mkdir -p filled_templates
      cat midway_split_geojson.sbatch | sed -e "s/::TYPE::/${type}/g" -e "s/::COUNTRYCODE::/${countrycode}/g" -e "s/::FILEPATH::/${file}/g"> filled_templates/${countrycode}_${type}.sbatch
      sbatch filled_templates/${countrycode}_${type}.sbatch
  fi 

done < $ALL_COUNTRIES
