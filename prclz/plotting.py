from itertools import cycle
from typing import Iterable, Iterator, List, Optional, Tuple

import matplotlib
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from shapely.geometry import Polygon

Color = Tuple[float, float, float]

# color schemes
def normalize(rgb: Tuple[int, int, int]) -> Color:
    r, g, b = rgb
    return (r/256.0, g/256.0, b/256.0)

def palette(colors: Iterable[Tuple[int, int, int]]) -> Iterator[Color]:
    return cycle(map(normalize, colors))

greens = palette([(180, 213, 202), (134, 188, 168), (94, 153, 131), (62, 101, 88)])

def plot_polygons(
    polygons: List[Polygon], 
    ax: Optional[matplotlib.axes.Axes] = None, 
    facecolors: Optional[Iterator[Color]] = None, 
    edgecolors: Optional[Iterator[Color]] = None, 
    linewidth: float=0.5, 
    zorder: int=10
) -> matplotlib.figure.Figure:
    if not ax:
        ax = plt.gca()
    if not facecolors:
        facecolors = cycle(['gray'])
    if not edgecolors:
        edgecolors = cycle(['white'])
    
    for (polygon, fc, ec) in zip(polygons, facecolors, edgecolors):
        ax.add_patch(PolygonPatch(polygon, fc=fc, ec=ec, linewidth=linewidth, zorder=zorder))
    plt.autoscale()

    return plt.gcf()
