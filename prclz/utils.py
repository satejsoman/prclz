from shapely.geometry import Polygon

def parse_ona_text(text: str) -> Polygon:
    str_coordinates = text.split(';')
    coordinates = [s.split() for s in str_coordinates]
    return Polygon([(float(x), float(y)) for (y, x, t, z) in coordinates])