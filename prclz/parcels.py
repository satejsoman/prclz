import logging
from typing import Optional, Sequence

import overpy
from shapely.geometry import Point

building_centroid_query = """
[out:json];
way[building]{bbox};
out ids center;
"""

full_body_query = """
[out:json];
way[building]{bbox};
(._;>;);
out ids center;
"""

def get_building_centroids(
    south: float, 
    west: float, 
    north: float, 
    east: float, 
    ovp: Optional[overpy.Overpass] = None
) -> Sequence[Point]:
    logging.info("Querying Overpass for building centroids.")
    if not ovp:
        ovp = overpy.Overpass()
    query = building_centroid_query.format(bbox=(south, west, north, east))
    result = ovp.query(query)
    logging.info("Overpass Query returned.")
    return [Point(float(way.center_lon), (float(way.center_lat))) for way in result.ways]
