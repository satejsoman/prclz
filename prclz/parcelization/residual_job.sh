
parcel_list=()
for i in data/parcels/Africa/*/*.geojson; do
    parcel_list+=("$i")
done
parcel_list=("${parcel_list[@]/parcels/geojson_gadm}")
parcel_list=("${parcel_list[@]/parcels/buildings}")
echo "${parcel_list[@]}"

building_list=()
for i in data/geojson_gadm/Africa/*/*.geojson; do
    building_list+=("$i")
done
echo "${building_list[@]}"

residual_list=()
residual_list=(`echo ${building_list[@]} ${parcel_list[@]} | tr ' ' '\n' | sort | uniq -u `)
echo "${residual_list[@]}"

printf '%s\n' "${residual_list[@]}"
