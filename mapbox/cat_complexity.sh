cd /project2/bettencourt/mnp/prclz/data/complexity

for i in $(ls -d *); do
head -1 /project2/bettencourt/mnp/prclz/mapbox/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv
find /project2/bettencourt/mnp/prclz/data/complexity/${i}/*/*.csv -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv 
    echo "$file"
done
ogr2ogr -f "GeoJSON" /project2/bettencourt/mnp/prclz/data/tilesets/${i}.geojson /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv 
done
