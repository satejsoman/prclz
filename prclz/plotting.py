from itertools import cycle
from types import SimpleNamespace
from typing import Iterable, Iterator, List, Optional, Tuple

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.geometry import Polygon

Color = Tuple[float, float, float]

# color schemes
def normalize(rgb: Tuple[int, int, int]) -> Color:
    r, g, b = rgb
    return (r/256.0, g/256.0, b/256.0)

def palette(colors: Iterable[Tuple[int, int, int]]) -> Iterator[Color]:
    return cycle(map(normalize, colors))

greens = palette([(180, 213, 202), (134, 188, 168), (94, 153, 131), (62, 101, 88)])

palettes = SimpleNamespace(**{
    "greens": greens
})

def plot_polygons(
    polygons: List[Polygon], 
    ax: Optional[matplotlib.axes.Axes] = None, 
    facecolors: Optional[Iterator[Color]] = None, 
    edgecolors: Optional[Iterator[Color]] = None, 
    linewidth: float=0.5, 
    zorder: int=10,
    alpha: float=1.0
) -> matplotlib.figure.Figure:
    if not ax:
        ax = plt.gca()
    if not facecolors:
        facecolors = cycle(['gray'])
    if not edgecolors:
        edgecolors = cycle(['white'])
    
    for (polygon, fc, ec) in zip(polygons, facecolors, edgecolors):
        ax.add_patch(PolygonPatch(polygon, fc=fc, ec=ec, linewidth=linewidth, zorder=zorder, alpha=alpha))
    plt.autoscale()

    return plt.gcf()

def colorbar(
    gdf: gpd.GeoDataFrame, 
    column: str, 
    title: Optional[str] = None, 
    cmap: Optional[str] = None
) -> matplotlib.figure.Figure:
    gdf.plot(column=column, cmap=cmap, legend=True)
    if title:
        plt.title(title)
    plt.gca().axis('off')
    return plt.gcf()
