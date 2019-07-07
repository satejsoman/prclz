from typing import Optional
import overpy


def query_buildings(south: float, west: float, north: float, east: float, ovp: Optional[overpy.Overpass] = None):
    if not ovp:
        ovp = overpy.Overpass()
    query = """
    [out:json];
    (
        node["building"="yes"]{bbox};
        way["building"="yes"]{bbox};   
        relation["building"="yes"]{bbox};
    );

    (._;>;);

    out body;
    """.format(bbox=(south, west, north, east))
    return ovp.query(query)

