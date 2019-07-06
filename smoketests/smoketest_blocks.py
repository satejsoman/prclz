import logging
from itertools import cycle

import matplotlib.pyplot as plt
from descartes import PolygonPatch
from shapely.geometry import box

from prclz.blocks.extraction import extract_blocks
from prclz.blocks.methods import intersection_polygonize

colors = cycle([
    tuple(_/256.0 for _ in rgb) for rgb in [
        [180, 213, 202],
        [134, 188, 168],
        [94, 153, 131],
        [62, 101, 88]
    ]
])

def ckg(): 
    xmin = -13.2995606518
    xmax = -13.1678762591
    ymin = 8.4584896524
    ymax = 8.5000670774
    bbox = box(xmin, ymin, xmax, ymax)

    blocks = extract_blocks(bbox)

    plt.figure()
    ax: matplotlib.axes.Axes = plt.gca()
    for (block, color) in zip(blocks, colors): 
        ax.add_patch(PolygonPatch(block, fc=color, ec='white', linewidth=0.5, zorder=10))
    plt.autoscale()
    plt.show()

def chicago():
    ymax = 41.8022
    xmin = -87.6064
    ymin = 41.7873
    xmax = -87.5758

    bbox = box(xmin, ymin, xmax, ymax)

    blocks = extract_blocks(bbox, extraction_method=intersection_polygonize)

    plt.figure()
    ax: matplotlib.axes.Axes = plt.gca()
    for (block, color) in zip(blocks, colors): 
        ax.add_patch(PolygonPatch(block, fc=color, ec='white', linewidth=0.5, zorder=10))
    plt.autoscale()
    plt.show()

if __name__ == "__main__":
    chicago()
