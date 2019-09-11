
# CONVERT CSVs to GEOJSON
module load intel/18.0
module load gdal/2.2
module load Anaconda3/5.1.0

# CONCATENATE CSVs
continent_list = ()
cd /project2/bettencourt/mnp/prclz/data/complexity
for i in $(ls -d */); do
	continent_list+=("$i")
	find /project2/bettencourt/mnp/prclz/data/complexity/${i}/* -name "*.csv" | while read file
	do
		head -1 ./Africa/SLE/complexity_SLE.3.4.10_1.csv > /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv
	    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv
	done
	python /project2/bettencourt/mnp/prclz/mapbox/mapbox_conversion.py "$i"
done
printf '%s\n' "${continent_list[@]}"


# DELETE TILESET SOURCE
curl -X DELETE "https://api.mapbox.com/tilesets/v1/sources/${MAPBOX_USERNAME}/${CONTINENT_FILE}?access_token=${MAPBOX_API_TOKEN}"

# CREATE TILESET SOURCE ID
curl -F file=@/Users/nmarchio/Desktop/sle_complexity_combined.geojson \
  "https://api.mapbox.com/tilesets/v1/sources/${MAPBOX_USERNAME}/${CONTINENT_FILE}?access_token=${MAPBOX_API_TOKEN}"

# CREATE TILESET RECIPE
curl -X POST "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${CONTINENT_FILE}?access_token=${MAPBOX_API_TOKEN}" \
  --header "Content-Type:application/json" \
  -d @- <<END;
{"recipe":
  {
    "version": 1,
    "layers": {
      "${CONTINENT_FILE}_zoomlayer1": {
        "source": "mapbox://tileset-source/nmarchi0/${CONTINENT_FILE}",
        "minzoom": 0,
        "maxzoom": 10
      },
      "${CONTINENT_FILE}_zoomlayer2": {
        "source": "mapbox://tileset-source/nmarchi0/${CONTINENT_FILE}",
        "minzoom": 11,
        "maxzoom": 13
      }
    }
  },
  "name": "${CONTINENT_FILE}"
} 
END

# PUBLISH TILESET SOURCE
curl -X POST "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${CONTINENT_FILE}/publish?access_token=${MAPBOX_API_TOKEN}"

# RETRIEVE STATUS
curl "https://api.mapbox.com/tilesets/v1/${MAPBOX_USERNAME}.${CONTINENT_FILE}/status?access_token=${MAPBOX_API_TOKEN}"



