
cd /project2/bettencourt/mnp/prclz/data/complexity

for i in $(ls -d *); do
head -1 /project2/bettencourt/mnp/prclz/data/complexity/Africa/SLE/complexity_SLE.3.4.10_1.csv > /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv
find /project2/bettencourt/mnp/prclz/data/complexity/${i}/*/*.csv -name "*.csv" | while read file
do 
    tail -n +2 -q $file >> /project2/bettencourt/mnp/prclz/data/tilesets/${i}.csv 
done
done
