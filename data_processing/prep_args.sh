#!/bin/sh

target_dir=$1
num_workers=$2

mkdir tmp

cur_wkr=0
for f in ${target_dir}/*buildings.geojson ; do
    echo $f >> tmp/wkr${cur_wkr}.txt
    echo "preupdate cur_wkr is $cur_wkr"
    ((cur_wkr++))    
    ((cur_wkr = cur_wkr % num_workers))
    echo "cur_wkr is $cur_wkr"
done


