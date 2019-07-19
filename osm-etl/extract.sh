#!/bin/bash  

pbf_path="$1"
temp0="${pbf_path/input/geojson}"
output_prefix="${temp0/-latest.osm.pbf}"


function extract() { 
    output_name="${output_prefix}_${1}.geojson"
    script="$2"

    echo "Loading pbf file: ${pbf_path}"
    echo "Saving geojson to: ${output_name}"
    echo ""

    OSM_CONFIG_FILE=osmconf.ini ogr2ogr -f GeoJSON ${output_name} ${pbf_path} -sql "${script}"
}

if [[ $(hostname) =~ ^midway* ]] ; then 
    echo "loading modules on $(hostname)"
    module load gdal/2.2
    module load python/3.6.1+intel-16.0
fi 

extract "lines"             "select * from lines where natural = 'coastline' or highway is not null or waterway is not null"
extract "buildings"         "select * from lines where building is not null"
extract "building_polygons" "select * from multipolygons where building is not null"

# OSM_CONFIG_FILE=osmconf.ini ogr2ogr -f GeoJSON ${output_prefix}_lines.geojson             ${pbf_path} -sql "select * from lines where natural = 'coastline' or highway is not null or waterway is not null"
# OSM_CONFIG_FILE=osmconf.ini ogr2ogr -f GeoJSON ${output_prefix}_buildings.geojson         ${pbf_path} -sql "select * from lines where building is not null"
# OSM_CONFIG_FILE=osmconf.ini ogr2ogr -f GeoJSON ${output_prefix}_building_polygons.geojson ${pbf_path} -sql "select * from multipolygons where building is not null"
