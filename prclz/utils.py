from logging import info, warning

import geopandas as gpd
from shapely.geometry import Polygon


def parse_ona_text(text: str) -> Polygon:
    str_coordinates = text.split(';')
    coordinates = [s.split() for s in str_coordinates]
    return Polygon([(float(x), float(y)) for (y, x, t, z) in coordinates])

def get_gadm_level_column(gadm: gpd.GeoDataFrame, level: int = 5) -> str:
    gadm_level_column = "GID_{}".format(level)
    while gadm_level_column not in gadm.columns and level > 0:
        warning("GID column for GADM level %s not found, trying with level %s", level, level-1)
        level -= 1
        gadm_level_column = "GID_{}".format(level)
    info("Using GID column for GADM level %s", level)
    return gadm_level_column, level
