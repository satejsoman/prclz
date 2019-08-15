
# Set up environment ------------------------------------------------------

library(sf)
library(tidyr)
library(dplyr)
library(purrr)
library(lwgeom)
library(argparse)

library(future)
library(parallel)
library(foreach)
library(doFuture)
library(doParallel)
library(batchtools)
library(future.batchtools)

plan(list(tweak(batchtools_slurm, 
                  template = "batchtools_slurm.tmpl", 
                  label = paste0('job_',make.names(Sys.time())),
                  resources = list(partition='broadwl',
                                   walltime='01:00:00',
                                   mem_per_cpu = '8G', 
                                   nodes = '1', 
                                   ntasks = '28',
                                   mail = 'nmarchio@uchicago.edu',
                                   pi_account = 'pi-bettencourt'),
                  workers = 28), 
            multiprocess))

# Parcelization function ------------------------------------------------

#' @param footprints, multirow dataframe, MULTIPOLYGON Simple feature collection of building footprints at country level
#' @param block, singlerow dataframe, POLYGON Simple feature collection
#' 
#' @return MULTILINE Simple feature collection
#'  
st_parcelize <- function(footprints, block){
  # Extract building polygons within specified block
  block_footprints <- footprints %>% 
    sf::st_convex_hull() %>%
    sf::st_difference() %>%
    lwgeom::st_make_valid() %>%
    sf::st_cast(to = "MULTIPOLYGON")
  # Convert building polygons to lines
  parcels = block_footprints %>%
    lwgeom::st_make_valid() %>%
    sf::st_union() %>% 
    sf::st_cast(., "POLYGON") %>% 
    sf::st_sf() %>%
    sf::st_cast(., "LINESTRING") %>%
    dplyr::mutate(id = row_number())
  # Add points along lines and cast to points
  parcelpoints = st_segmentize(parcels, units::set_units(100,m)) %>%
    sf::st_cast(., "MULTIPOINT") %>%
    sf::st_sf() %>%
    dplyr::mutate(id = parcels$id)
  # Voronoi polygon tesselation
  parcel_voronoi = parcelpoints %>% 
    sf::st_union()  %>%
    sf::st_voronoi()   %>% 
    sf::st_cast() %>% 
    sf::st_intersection(block) %>% 
    sf::st_sf()
  # Join with building ID
  parcel_voronoi = parcel_voronoi %>% 
    sf::st_join(., parcelpoints) %>%
    dplyr::filter(!is.na(id)) 
  # Group by the parcel ID to dissolve geometries 
  parcel_voronoi = raster::aggregate(parcel_voronoi, list(ID = parcel_voronoi$id), raster::unique)
  # Convert it back to lines
  parcel_grid = parcel_voronoi %>% 
    sf::st_cast("MULTILINESTRING") %>% 
    sf::st_geometry() %>% 
    sf::st_sf() %>%
    sf::st_difference() %>% 
    sf::st_union() %>% 
    sf::st_sf() %>%
    dplyr::mutate(block_id = block$block_id)
  return(parcel_grid)
}

# Read in command line arguments
args <- R.utils::commandArgs(trailingOnly = TRUE)
blocks_file <- args[1]
buildings_file <- args[2]
parcelization_file <- args[3]

cat(sprintf("Reading blocks %s.\n",blocks_file))
cat(sprintf("Reading buildings %s.\n",buildings_file))

# Load blocks and buildings spatial dataframes
sf_df_blocks <- sf::st_read(blocks_file) %>% 
  sf::st_as_sf(., wkt = 'geometry') %>% 
  sf::st_set_crs(sf::st_crs(4326)) 
sf_df_buildings <- sf::st_read(buildings_file) 

# Join block groupings into buildings spatial dataframes
sf_df <- df::st_join(x = sf_df_buildings, y = sf_df_blocks) %>% 
  dplyr::select(osm_id, block_id)

# Split buildings and blocks
split_buildings <- split(sf_df, sf_df$block_id) 
split_blocks <- split(gadm_blocks, gadm_blocks$block_id) 

# Parallelize computation across blocks to generate parcel geometries
sf_df_parcels <- foreach(i=split_buildings, j = split_blocks, .combine=rbind) %dopar% 
  st_parcelize(footprints = i, block = j)

# Write GADM-level spatial df containing block-level parcels
st_write(sf_df_parcels, paste0('/project2/bettencourt/mnp/prclz/data/parcels/',continent,'/',country_code,'/parcels_',gadm_code,'.geojson'))
