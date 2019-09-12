cd /project2/bettencourt/mnp/prclz/data/complexity

for i in $(ls -d *); do
head -1 /project2/bettencourt/mnp/prclz/mapbox/header.csv > /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv
find /project2/bettencourt/mnp/prclz/data/complexity/${i}/*/*.csv -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv 
done
done

module load intel/18.0
module load gdal/2.2
module load Anaconda3/5.1.0
