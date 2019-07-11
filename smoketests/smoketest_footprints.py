import overpy

from prclz.plotting import plot_polygons
from prclz.parcels import get_building_centroids

if __name__ == "__main__":
    xmin = west = -87.6064
    xmax = east = -87.5758
    ymin = south = 41.7873
    ymax = north = 41.8022
    r = get_building_centroids(ymin, xmin, ymax, xmax)
    print(r)

    centroids = [(w.center_lat, w.center_lon) for w in r.ways]
    