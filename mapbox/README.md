
## Mapbox ETL ##

* `tippencanoe` [package](https://github.com/mapbox/tippecanoe)
* [How to access OSM building via Mapbox](https://github.com/mapbox/malaria-mapping)
* [Mapbox API upload docs](https://docs.mapbox.com/api/maps/#datasets)


# Build tippecanoe from the source repository
git clone https://github.com/mapbox/tippecanoe.git
cd tippecanoe
make -j
make install

# Set current directory
cd /project2/bettencourt/mnp/prclz

# Make directory
mkdir /project2/bettencourt/mnp/prclz/data/mapbox/Africa/SLE
