#!/bin/bash

#SBATCH --job-name=csv_to_geojson
#SBATCH --partition=broadwl
#SBATCH --ntasks-per-node=1
#SBATCH --mem=56000
#SBATCH --output=logs/csv_to_geojson.out
#SBATCH --error=logs/csv_to_geojson.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nmarchio@uchicago.edu
#SBATCH --time=5:00:00
#SBATCH --account=rcc-staff

module load udunits/2.2
module load gdal/2.4.1 

