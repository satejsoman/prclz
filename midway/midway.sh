#!/bin/bash

set -e

echo "setting up modules on: $(hostname)"
module load intel/18.0
module load gdal/2.2
module load Anaconda3/5.1.0

echo "setting up conda"
conda create  --name mnp -f -y -q
conda config --append channels conda-forge
conda config --append channels anaconda
conda install --name mnp -f -y -q -c anaconda -c conda-forge --file ../requirements.txt
conda upgrade numpy --name mnp -f -y -q 

conda activate mnp 
