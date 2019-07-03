from typing import Callable
from shapely.geometry import Polygon, MultiLineString, MultiPolygon

BlockExtractionMethod = Callable[[Polygon, MultiLineString], MultiPolygon]
