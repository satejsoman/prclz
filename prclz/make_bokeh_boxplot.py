import numpy as np
import geopandas as gpd 
import sys 
sys.path.insert(0, "prclz")
from view import load_aoi
from pathlib import Path 

from bokeh.layouts import gridplot
from bokeh.models import BoxSelectTool, LassoSelectTool, ColumnDataSource, Circle, Slider
from bokeh.plotting import curdoc, figure, save 
from bokeh.io import show 

def get_point_coords(point, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return point.x
    elif coord_type == 'y':
        return point.y

# Prep data source
aoi_path = Path('../data/LandScan_Global_2018/aoi_datasets/analysis_nairobi.csv')

def make_box_plots(aoi_name, file_path, output_filename):

    title = "Complexity and other measures summary - {}".format(aoi_name)
    gdf = load_aoi(file_path)
    gt1 = gdf['bldg_density'] > 1
    gdf = gdf.loc[~gt1]
    cols = ['block_id', 'bldg_count', 'complexity', 'bldg_density', "block_area_km2", "total_bldg_area_sq_km"]

    TOOLS = "pan,wheel_zoom,box_select,lasso_select,hover,reset"
    FIG_W = 700
    FIG_H = 500 #700
    data = gdf[cols]
    data_source = ColumnDataSource(data)

    NOSELECTED_ALPHA = 0
    selected_circle = Circle(fill_alpha=1, fill_color="blue", line_color=None)
    nonselected_circle = Circle(fill_alpha=NOSELECTED_ALPHA, fill_color="blue", line_color=None)

    #slider = Slider(start=0.0, end=1, step=0.01, value=0.2)
    #slider.js_link('value', nonselected_circle, 'fill_alpha')

    p00 = figure(tools=TOOLS, x_axis_label='Building density', y_axis_label='Complexity', plot_width=FIG_W, plot_height=FIG_H, title="{}\nbldg_density".format(title))
    g00 = p00.circle(y='complexity', x='bldg_density', fill_alpha=0.5, size=10, hover_color="firebrick", source=data_source)
    g00.selection_glyph = selected_circle
    g00.nonselection_glyph = nonselected_circle

    p01 = figure(tools=TOOLS, x_axis_label='Block area (km2)', y_axis_label='Complexity', plot_width=FIG_W, y_range=p00.y_range, plot_height=FIG_H, title="block_area_km2")
    g01 = p01.circle(y='complexity', x='block_area_km2', fill_alpha=0.5, size=10, hover_color="firebrick", source=data_source)
    g01.selection_glyph = selected_circle
    g01.nonselection_glyph = nonselected_circle

    p10 = figure(tools=TOOLS, x_axis_label='Building count', y_axis_label='Complexity', plot_width=FIG_W, y_range=p00.y_range, plot_height=FIG_H, title="bldg_count")
    g10 = p10.circle(y='complexity', x='bldg_count', fill_alpha=0.5, size=10, hover_color="firebrick", source=data_source)
    g10.selection_glyph = selected_circle
    g10.nonselection_glyph = nonselected_circle

    p11 = figure(tools=TOOLS, x_axis_label='Total building area (km2)', y_axis_label='Complexity', plot_width=FIG_W, y_range=p00.y_range, plot_height=FIG_H, title="total_bldg_area_sq_km")
    g11 = p11.circle(y='complexity', x='total_bldg_area_sq_km', fill_alpha=0.5, size=10, hover_color="firebrick", source=data_source)
    g11.selection_glyph = selected_circle
    g11.nonselection_glyph = nonselected_circle

    p = gridplot([[p00, p01],
                  [p10, p11]])
    save(p, output_filename)


aoi_dir = Path("../data/LandScan_Global_2018/aoi_datasets/")
# make_ridge_plot(aoi_name, file_path, output_filename)

aoi_names = ['Freetown', 'Monrovia', 'Kathmandu', 'Nairobi', 'Port au Prince']
stubs = ['freetown', 'greater_monrovia', 'kathmandu', 'nairobi', 'port_au_prince']
file_names = ['analysis_{}.csv'.format(n) for n in stubs]
file_paths = [aoi_dir / f for f in file_names]
output_dir = Path("./bokeh_box_plots")
output_dir.mkdir(parents=True, exist_ok=True)
output_filenames = [output_dir / (n.replace(".csv", "_boxplot.html")) for n in file_names]

for aoi_name, file_path, output_filename in zip(aoi_names, file_paths, output_filenames):
    print("aoi_name = {}".format(aoi_name))
    print("file_path = {}".format(file_path))
    print("output_filename = {}".format(output_filename))
    make_box_plots(aoi_name, file_path, output_filename)
     


# gdf = gpd.read_file('reblock_sle_lbr_hti.geojson')
# gdf['centroids'] = gdf['geometry'].centroid 
# gdf['x'] = gdf['centroids'].apply(lambda p: get_point_coords(p, 'x'))
# gdf['y'] = gdf['centroids'].apply(lambda p: get_point_coords(p, 'y'))


# TOOLS="pan,wheel_zoom,box_select,lasso_select,reset"

# # Make first figure
# p0 = figure(tools=TOOLS, plot_width=600, plot_height=600, min_border=10, min_border_left=50,
#            toolbar_location="above", x_axis_location=None, y_axis_location=None,
#            title="Linked Histograms")
# p0.background_fill_color = "#fafafa"
# p0.select(BoxSelectTool).select_every_mousemove = False
# p0.select(LassoSelectTool).select_every_mousemove = False

# bokeh_df = gdf.drop(columns=['geometry', 'centroids'])
# bokeh_data_source = ColumnDataSource(bokeh_df)

# r = p.scatter('x', 'y', source=bokeh_data_source, size=3, color="#3A5785", alpha=0.6)

# # Make second figure
# p1 = figure(plot_width=600, plot_height=600, min_border=10, min_border_left=50,
#            x_axis_location=None, y_axis_location=None)

