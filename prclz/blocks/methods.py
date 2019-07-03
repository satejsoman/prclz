from shapely.geometry import MultiLineString, MultiPolygon, Polygon
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
    return extract


def intersection_polygonize() -> BlockExtractionMethod:
    def extract(region: Polygon, linestrings: MultiLineString) -> MultiPolygon:
        # add the region boundary as an additional constraint
        constrained_linestrings = linestrings + [region.exterior]
        return MultiPolygon(list(polygonize(constrained_linestrings)))
    return extract


DEFAULT_EXTRACTION_METHOD = buffered_line_diff()
