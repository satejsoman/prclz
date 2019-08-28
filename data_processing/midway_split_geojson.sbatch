#!/bin/bash

#SBATCH --job-name=::TYPE::_SPLIT_::COUNTRYCODE::
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=5
#SBATCH --mem=56000
#SBATCH --output=../logs/::TYPE::_SPLIT_::COUNTRYCODE::.out
#SBATCH --error=../logs/::TYPE::_SPLIT_::COUNTRYCODE::.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cnederhood@uchicago.edu
#SBATCH --time=04:00:00
#SBATCH --account=pi-bettencourt

set -e

python3 split_geojson.py ::FILEPATH:: --replace
