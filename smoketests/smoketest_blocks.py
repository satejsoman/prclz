import logging

import matplotlib  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from descartes import PolygonPatch  # type: ignore
from shapely.geometry import box  # type: ignore

from prclz.blocks.extraction import extract_blocks
from prclz.blocks.methods import (BufferedLineDifference,
                                  IntersectionPolygonization)
from prclz.plotting import greens as palette
from prclz.plotting import plot_polygons


def ckg(): 
    xmin = -13.2995606518
    xmax = -13.1678762591
    ymin = 8.4584896524
    ymax = 8.5000670774
    bbox = box(xmin, ymin, xmax, ymax)

    blocks = extract_blocks(bbox)
    plot_polygons(blocks)
    plt.show()

def chicago():
    xmin = -87.6064
    xmax = -87.5758
    ymin = 41.7873
    ymax = 41.8022
    bbox = box(xmin, ymin, xmax, ymax)

    blocks = extract_blocks(bbox)
    plot_polygons(blocks)
    plt.show()

if __name__ == "__main__":
    logging.basicConfig()
    chicago()
