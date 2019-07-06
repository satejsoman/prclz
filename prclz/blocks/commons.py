from typing import Callable, Tuple
from shapely.geometry import Polygon, MultiLineString, MultiPolygon

BlockExtractionMethod = Tuple[str, Callable[[Polygon, MultiLineString], MultiPolygon]]
