from shapely.geometry import (MultiLineString, MultiPolygon, Polygon, asShape,
                              mapping)
from shapely.ops import polygonize

from .commons import BlockExtractionMethod

# these could potentially be instances of a BlockExtractionMethod class,
# which in turn would be an AbstractBaseClass, but readability is too
# low to justify that approach


def buffered_line_diff(epsilon: float = 0.000005) -> BlockExtractionMethod:
    # https://gis.stackexchange.com/a/58674
    # suggest epsilon of 0.0001 for generating graphics,
    # and 0.00005 to generate shapefiles
    def extract(region: Polygon, linestrings: MultiLineString) -> MultiPolygon:
        return region.difference(linestrings.buffer(epsilon))
    return ("buffered line difference", extract)


def intersection_polygonize() -> BlockExtractionMethod:
    # https://peteris.rocks/blog/openstreetmap-city-blocks-as-geojson-polygons/#mapzen-metro-extracts
    def get_line_feature(start, stop, properties):
        return {"type": "Feature",
                "properties": properties, 
                "geometry": {
                    "type": "LineString",
                    "coordinates": [start, stop]
                }
            }
    
    def segment_streets(multipoint_lines):
        output = {
            "type": "FeatureCollection",
            "features": []
        }

        for feature in multipoint_lines['features']:
            output['features'] += [
                get_line_feature(current, feature['geometry']['coordinates'][i+1], feature['properties']) 
                for (i, current) in enumerate(feature['geometry']['coordinates'][:-1])]
        return output

    def polygonize_streets(streets):
        lines = []
        for feature in streets['features']:
            lines.append(asShape(feature['geometry']))

        polys = list(polygonize(lines))

        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        for poly in polys:
            geojson['features'].append({
                "type": "Feature",
                "properties": {},
                "geometry": mapping(poly)
            })

        return geojson
    
    def extract(region: Polygon, linestrings: MultiLineString) -> MultiPolygon:
        segmented_streets = segment_streets(linestrings)
        # add the region boundary as an additional constraint
        constrained_linestrings = linestrings + [region.exterior]
        return MultiPolygon(list(polygonize(constrained_linestrings)))
    
    return ("intersection polygonization", extract)


DEFAULT_EXTRACTION_METHOD = buffered_line_diff
