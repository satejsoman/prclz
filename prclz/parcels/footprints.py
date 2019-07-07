from typing import Optional
import overpy

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

def query_buildings(south: float, west: float, north: float, east: float, ovp: Optional[overpy.Overpass] = None):
    if not ovp:
        ovp = overpy.Overpass()
    query = building_centroid_query.format(bbox=(south, west, north, east))
    return ovp.query(query)

