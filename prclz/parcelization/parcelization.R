library(sf)
library(tidyr)
library(dplyr)
library(purrr)
library(lwgeom)
library(parallel)
library(rslurm)

# Extract block parcels ------------------------------------------------

#' @param footprints, multirow dataframe, MULTIPOLYGON Simple feature collection of building footprints at country level
#' @param block, singlerow dataframe, POLYGON Simple feature collection
#' 
#' @return MULTILINE Simple feature collection 
extract_block_parcels <- function(footprints, block){
  # Extract building polygons within specified block
  block_footprints <- sf::st_intersects(footprints, block, sparse = F) %>%
    base::cbind(footprints, 'keep' = .) %>%
    dplyr::filter(keep == TRUE) %>%
    sf::st_convex_hull() %>%
    sf::st_difference() %>%
    lwgeom::st_make_valid() %>%
    sf::st_cast(to = "MULTIPOLYGON")
  # Convert building polygons to lines
  parcels = block_footprints %>%
  #parcels = footprints %>%
    lwgeom::st_make_valid() %>%
    sf::st_union() %>% 
    sf::st_cast(., "POLYGON") %>% 
    sf::st_sf() %>%
    sf::st_cast(., "LINESTRING") %>%
    dplyr::mutate(id = row_number())
  # Add points along lines and cast to points
  parcelpoints = st_segmentize(parcels, 1) %>%
    sf::st_cast(., "MULTIPOINT") %>%
    sf::st_sf() %>%
    dplyr::mutate(id = parcels$id)
  # Voronoi polygon tesselation and cut to block
  parcel_voronoi = parcelpoints %>% 
    sf::st_union() %>%
    sf::st_voronoi() %>% 
    sf::st_cast() %>% 
    sf::st_intersection(block) %>% 
    sf::st_sf()
  # Join with building IDs
  parcel_voronoi = parcel_voronoi %>% 
    sf::st_join(., parcelpoints) %>%
    dplyr::filter(!is.na(id)) 
  # Group by the parcel ID to dissolve geometries 
  parcel_voronoi = raster::aggregate(parcel_voronoi, list(ID = parcel_voronoi$id), raster::unique)
  # Convert geometry back to lines
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
