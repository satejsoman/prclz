#!/bin/bash

echo "setting up modules on: $(hostname)"
module load intel/18.0
module load gdal/2.2
module load Anaconda3/5.1.0

conda update -n base -c defaults conda
conda create --name mnp 
conda install -f -y -q --name mnp -c conda-forge --file ../requirements.txt
conda upgrade numpy 

conda activate mnp 