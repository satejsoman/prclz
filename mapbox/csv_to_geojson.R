
library(sf)
library(dplyr)

df_mb <- sf::st_read('/project2/bettencourt/mnp/prclz/data/tilesets/global_file.csv') %>% sf::st_as_sf(., wkt = 'geometry') %>% sf::st_set_crs(sf::st_crs(4326)) %>% dplyr::select(block_id, complexity)
sf::st_write(obj = df_mb, dsn = paste0('/project2/bettencourt/mnp/prclz/data/tilesets/global_file.geojson'), delete_dsn = TRUE)
