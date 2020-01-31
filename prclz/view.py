import typing 

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon, MultiLineString, Point, LineString
from shapely.ops import cascaded_union
from shapely.wkt import loads
import pandas as pd
import geopandas as gpd 
import numpy as np 
import time 

import os 
import matplotlib.pyplot as plt 
import sys 

import argparse
import igraph

import i_topology_utils
from i_topology import *
import time 

from pathlib import Path  
from shapely.wkt import loads 
import ast 

DATA = Path("../data")
REBLOCK = DATA / "reblock"
REBLOCK_VIEWIING = DATA / 'reblock_viewing'
sys.path.insert(0, "../")
from data_processing import process_worldpop
sys.path.insert(0, "../analysis")
import aoi_analysis

# region = "Africa"
# gadm_code = "SLE"
# gadm = "SLE.4.2.1_1"
# example_block = "SLE.4.2.1_1_1241"

# REBLOCK = "../data/reblock/Africa/LBR"

# # (1) Just load our data for one GADM
# print("Begin loading of data")
# blocks = i_topology_utils.csv_to_geo(os.path.join("../data", "blocks", region, gadm_code, "blocks_"+gadm+".csv"))

# # # (2) Now build the parcel graph and prep the buildings
# # # restrict to some example blocks within the GADM
# block = blocks[blocks['block_id']==example_block]

# steiner = gpd.read_file("test_SLE_igraph/steiner_lines.geojson")
# terminal = gpd.read_file("test_SLE_igraph/terminal_points.geojson")

# Bokeh import 
from bokeh.plotting import figure, save
from bokeh.models import GeoJSONDataSource, ColumnDataSource, HoverTool, LinearColorMapper
from bokeh.palettes import RdYlBu11, RdYlGn11, Viridis11
from bokeh.io import output_notebook, output_file, show 

MNP = ["#0571b0", "#f7f7f7", "#f4a582", "#cc0022"]
#MNP = ["#cc0022", "#f4a582", "#f7f7f7", "#0571b0"]
PALETTE = MNP
#RANGE = [(0,1), (2,3), (4,7), (8, np.inf)]
RANGE = [1, 3, 7, np.inf]
RANGE_LABEL = ['high', 'medium', 'low', 'very low']
MATCHED = ['high (<=1)', 'medium (<=3)', 'low (<=7)', 'very low (<=inf)']
for upper, label in zip(RANGE, RANGE_LABEL):
    stub = " (<={})".format(upper)
    MATCHED += (label + stub)

def get_range(complexity):
    for upper, label in zip(RANGE, RANGE_LABEL):
        if complexity <= upper:
            stub = " (<={})".format(upper)
            return label + stub 

def get_point_coords(point, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return point.x
    elif coord_type == 'y':
        return point.y

def get_line_coords(line, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return line.coords.xy[0]
    elif coord_type == 'y':
        return line.coords.xy[1]

def get_polygon_coords(polygon, coord_type):
    """Calculates coordinates ('x' or 'y') of a Point geometry"""
    if coord_type == 'x':
        return list(polygon.exterior.coords.xy[0])
    elif coord_type == 'y':
        return list(polygon.exterior.coords.xy[1])

def get_multipolygon_coords(multipolygon, coord_type):
    rv = []
    if multipolygon is None:
        return None 
    for poly in multipolygon:
        if coord_type == 'x':
            rv += get_polygon_coords(poly, 'x')
        else:
            rv += get_polygon_coords(poly, 'y')
    return rv 
  
def make_bokeh(complexity_df, output_filename):
    # c is a complexity geodataframe
    # (1) Process the data sources

    output_file(output_filename.split(".")[0])
    cols = ['block_id', 'bldg_count', 'block_area_km2', 'complexity', 'bldg_density']

    # 1.a -- define blocks
    df_blocks = complexity_df[cols].copy()
    #print("df blocks CRS = {}".format(df_blocks.crs))
    g = complexity_df['geometry'].to_crs({'init': 'epsg:3395'})
    df_blocks['x'] = g.apply(lambda p: get_polygon_coords(p, 'x'))
    df_blocks['y'] = g.apply(lambda p: get_polygon_coords(p, 'y'))

    # 1.b -- define hover tool
    my_hover = HoverTool()
    cols_in_hover = ['block_id', 'complexity', 'bldg_count', 'block_area_km2', 'bldg_density']
    cols_label =    ['Block ID', 'Complexity', 'Building count', 'Block area (km2)', 'Density']
    my_hover.tooltips = [(l, "@"+c) for l,c in zip(cols_label, cols_in_hover)]

    # 1.c -- define buildings
    df_buildings = ComplexityViewer.make_building_geom(complexity_df)
    missing = df_buildings['geometry'].isna()
    df_buildings = df_buildings.loc[~missing]
    df_buildings = df_buildings.explode()
    df_buildings['geometry'].crs = {'init': 'epsg:4326'}
    df_buildings.crs = {'init': 'epsg:4326'}
    df_buildings['geometry'] = df_buildings['geometry'].to_crs({'init': 'epsg:3395'})
    df_buildings['x'] = df_buildings['geometry'].apply(lambda p: get_polygon_coords(p, 'x'))
    df_buildings['y'] = df_buildings['geometry'].apply(lambda p: get_polygon_coords(p, 'y'))
    df_buildings_no_geom = df_buildings.drop(columns=['geometry'])
    #missing = df_buildings_no_geom['x'].isna()
    #source_df_buildings = ColumnDataSource(df_buildings_no_geom.loc[~missing])

    
    df_blocks['compl_label'] = df_blocks['complexity'].apply(get_range)
    
    # (2) Make the fig
    fig = figure(border_fill_color='blue', border_fill_alpha=0.25, match_aspect=True, aspect_scale=1.0,
                 plot_height=800, plot_width=1600, x_axis_type="mercator", y_axis_type="mercator")

    # 2.a -- add the tools
    fig.add_tools(my_hover)

    # (3) Assemble the plot
    #color_mapper = LinearColorMapper(palette=PALETTE)
    #source_df_blocks = ColumnDataSource(df_blocks)
    #fig.patches('x', 'y', fill_color={'field': 'complexity', 'transform':color_mapper}, source=source_df_blocks)

    # Legend plot of blocks
    labels = MATCHED
    for label, color in zip(labels, MNP):
        cur_df = df_blocks.loc[df_blocks['compl_label']==label]
        cur_source = ColumnDataSource(cur_df)
        fig.patches('x', 'y', fill_color=color, source=cur_source, legend=label)

    # Legend plot of buildings
    #source_df_buildings = ColumnDataSource(df_buildings_no_geom)
    df_buildings_no_geom['compl_label'] = df_buildings_no_geom['complexity'].apply(get_range)
    for label, color in zip(labels, MNP):
        cur_df = df_buildings_no_geom.loc[df_buildings_no_geom['compl_label']==label]
        cur_source = ColumnDataSource(cur_df)
        fig.patches('x', 'y', line_alpha=0, fill_color='black', fill_alpha=0.3, source=cur_source, legend=label)

    #fig.patches('x', 'y', line_width=0, fill_color='black', fill_alpha=0.3, source=source_df_buildings)

    fig.legend.location = "top_left"
    fig.legend.click_policy="hide"
    
    #save(fig, output_filename)
    show(fig)

# MNP = ["#0571b0", "#f7f7f7", "#f4a582", "#cc0022"]
# PALETTE = MNP
# #RANGE = [(0,1), (2,3), (4,7), (8, np.inf)]
# RANGE = [1, 3, 7, np.inf]
# RANGE_LABEL = ['high', 'medium', 'low', 'very low']

def convert_buildings(bldg_obs):
    '''
    Converts the literal string repr list of wkt format
    to multipolygons
    '''

    try:
        bldg_list = ast.literal_eval(bldg_obs)
        bldgs = [loads(x) for x in bldg_list]
        return MultiPolygon(bldgs)
    except:
        return None 

def make_scatter_plot(df_path, count_var='bldg_count'):
    df = pd.read_csv(df_path)
    s_time_mins = df['steiner_time'].values / 60
    #count = df['bldg_count'].values
    #count = df['edge_count_post'].values
    df['bldg_count'] = df[count_var]
    count = df[count_var].values

    plt.scatter(count, s_time_mins, color='red', alpha=0.3)
    plt.title("Steiner optimal path time per block (mins)")
    plt.xlabel("Buildings in block")
    plt.ylabel("Compute time (mins)")

    return df 

def line_graph_xy(df_path, count_var='bldg_count'):
    df = pd.read_csv(df_path)
    df['bldg_count'] = df[count_var]
    #count = df['bldg_count'].values
    #count = df['edge_count_post'].values
    g_df = df[['steiner_time', 'bldg_count']].groupby('bldg_count').mean()
    g_df.sort_index(inplace=True)
    g_df['steiner_time'] = g_df['steiner_time'] / 60
    x = g_df.index.values
    y = g_df['steiner_time'].values
    return g_df, x, y 

gadm_list = ['KEN.30.10.1_1', 'KEN.30.10.2_1', 'KEN.30.10.3_1', 'KEN.30.10.4_1',
             'KEN.30.10.5_1', 'KEN.30.11.2_1']


def read_steiner(path):
    wkt_to_geom = lambda x: loads(x) if isinstance(x, str) else None 

    d = pd.read_csv(path).drop(columns=['Unnamed: 0'])
    d['geometry'] = d['geometry'].apply(wkt_to_geom)
    geo_d = gpd.GeoDataFrame(d)

    return geo_d 

def process_complexity_pop(df):
    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geometry'].apply(loads)
    gdf.geometry.crs = {'init': 'epsg:4326'}  
    gdf.crs = {'init': 'epsg:4326'}
    gdf['is_neg_pop'] = gdf['pop_est'] < 0
    gdf['bldg_density'] = gdf['total_bldg_area_sq_km'] / gdf['block_area_km2']
    gdf['gt1'] = gdf['bldg_density'] > 1
    return gdf 

def load_complexity_pop(region, country_code, gadm):
    landscan_path = DATA / 'LandScan_Global_2018' / region / country_code
    complexity_pop_path = landscan_path / "complexity_pop_{}.csv".format(gadm) 
    df = pd.read_csv(complexity_pop_path)
    #print("There are {} gt 1".format(gt1.sum()))    #gdf.drop(columns=['Unnamed: 0'], inplace=True)
    return process_complexity_pop(df)  

def load_aoi(aoi_path):
    df = pd.read_csv(aoi_path)
    return process_complexity_pop(df)  

def get_most_dense_within_complexity_level(df, complexity, count):

    comp_bool = df['complexity'] == complexity
    sub_df = df.loc[comp_bool]
    rv = sub_df.sort_values('bldg_density', inplace=False, ascending=False)
    return rv.iloc[0:count]['block_id'].values

def get_blocks_with(df, complexity=None, density_range=[0, 1]):

    c_bool = df['complexity'] == complexity
    b = c_bool & (df['bldg_density'] <= density_range[1]) & (df['bldg_density'] >= density_range[0])
    return sub_df['block_id'][b].values

class ComplexityViewer:

    def __init__(self, gadm_list=None, aoi_path=None, region=None, block_list=None):

        self.gadm_code = gadm_list[0][0:3] if gadm_list is not None else None
        self.region = region 
        self.gadm_list = gadm_list
        self.block_list = block_list
        self.gadm_count = len(gadm_list) if gadm_list is not None else None 
        self.complexity = ComplexityViewer.load_complexity(region, self.gadm_code, aoi_path)
        #self.complexity = pd.concat([load_complexity_pop(region, self.gadm_code, gadm) for gadm in gadm_list])        
        self.buildings = ComplexityViewer.make_building_geom(self.complexity)
        self.block_ids = self.complexity['block_id']

    @staticmethod
    def load_complexity(region, gadm_code, aoi_path):

        if aoi_path is not None:
            rv = load_aoi(aoi_path)
        else:
            rv = pd.concat([load_complexity_pop(region, self.gadm_code, gadm) for gadm in gadm_list])

        rv['gadm'] = rv['block_id'].apply(lambda s: s[0:s.rfind("_")])
        return rv 

    @staticmethod
    def make_building_geom(gdf):
        buildings = gdf['geometry_bldgs'].apply(convert_buildings)
        comp = gdf['complexity'].values 
        #buildings['complexity'] = comp
        buildings_gdf = gpd.GeoDataFrame({"geometry":buildings, "block_id":gdf['block_id']})
        buildings_gdf['gadm'] = buildings_gdf['block_id'].apply(lambda s: s[0:s.rfind("_")])
        buildings_gdf['complexity'] = comp
        return buildings_gdf

    @staticmethod
    def from_block_list(block_list, region):
        '''
        Allows for construction via a list of blocks rather than gadms
        '''
        gadm_list = {s[0:s.rfind("_")] for s in block_list}
        gadm_list = list(gadm_list)

        return ComplexityViewer(gadm_list=gadm_list, region=region, block_list=block_list)

    def restrict(self, gadm_aois=None, block_aois=None):
        def restrict_to_aois(df):
            if block_aois is None and gadm_aois is None:
                return df 
            else:
                aoi_type = 'block_id' if block_aois is not None else 'gadm'
                aois = block_aois if aoi_type == "block_id" else gadm_aois

                aoi_df = pd.DataFrame({aoi_type: aois})
                print(aoi_df.columns)
                df_sub = df.merge(aoi_df, how='left', on=aoi_type, indicator='in_aoi')
                in_aoi_bool = df_sub['in_aoi'] == 'both'
                print("overlap")
                print(in_aoi_bool.sum())
                return df_sub.loc[in_aoi_bool]

        cur_complexity = restrict_to_aois(self.complexity)
        return cur_complexity


    def view(self, gadm_aois=None, block_aois=None, add_buildings=True, annotate_density=False,
                   annotate_block_id=False, save_to=None):
        
        def restrict_to_aois(df):
            if block_aois is None and gadm_aois is None:
                return df 
            else:
                aoi_type = 'block_id' if block_aois is not None else 'gadm'
                aois = block_aois if aoi_type == "block_id" else gadm_aois

                aoi_df = pd.DataFrame({aoi_type: aois})
                print(aoi_df.columns)
                df_sub = df.merge(aoi_df, how='left', on=aoi_type, indicator='in_aoi')
                in_aoi_bool = df_sub['in_aoi'] == 'both'
                print("overlap")
                print(in_aoi_bool.sum())
                return df_sub.loc[in_aoi_bool]
        
        cur_complexity = restrict_to_aois(self.complexity)
        missing_complexity = cur_complexity['complexity'].isna()
        ax = cur_complexity.loc[~missing_complexity].plot(column='complexity', legend=True, figsize=(15,15))
        cur_complexity.loc[missing_complexity].plot(color='black', alpha=0.1, ax=ax)
        #ax = cur_complexity.plot( legend=True, figsize=(15,15))

        if add_buildings:
            restrict_to_aois(self.buildings).plot(color='black', alpha=0.4, ax=ax)

        # add labels
        if annotate_density or annotate_block_id:
            centroids = cur_complexity.centroid
            zipped = zip(cur_complexity.block_id, cur_complexity.bldg_density, centroids.x, centroids.y)
            for block, density, x, y in zipped:
                if annotate_density and annotate_block_id:
                    text = "{}\n{}".format(block, np.round(density, 4))
                else:
                    text = str(block) if annotate_block_id else str(np.round(density, 4))
                ax.annotate(text, (x,y))

        if save_to:
            #fig = plt.gcf()
            #fig.set_size_inches
            plt.savefig(str(save_to))

    
class ReblockPlotter:

    def __init__(self, gadm_list, region, block_list=None, add_complexity=False, add_reblock=False, add_buildings=False, add_parcels=False):

        self.gadm_code = gadm_list[0][0:3]
        self.region = region 
        self.gadm_list = gadm_list
        self.block_list = block_list
        self.gadm_count = len(gadm_list)
        self.add_buildings = add_buildings
        self.add_parcels = add_parcels
        self.add_reblock = add_reblock
        self.add_complexity = add_complexity

        reblock_path = REBLOCK / self.region
        
        for j, gadm in enumerate(self.gadm_list):

            blocks_path = DATA / "blocks" / region / self.gadm_code / "blocks_{}.csv".format(gadm)
            buildings_path = DATA / "buildings" / region / self.gadm_code / "buildings_{}.geojson".format(gadm)
            parcels_path = DATA / "parcels" / region / self.gadm_code / "parcels_{}.geojson".format(gadm)
            steiner_path = DATA / "reblock" / region / self.gadm_code / "steiner_lines_{}.csv".format(gadm)
            terminal_path = DATA / "reblock" / region / self.gadm_code / "terminal_points_{}.csv".format(gadm)
            complexity_path = DATA / "complexity" / region / self.gadm_code / "complexity_{}.csv".format(gadm)

            if j == 0:
                self.blocks = i_topology_utils.csv_to_geo(blocks_path)
                self.complexity = process_worldpop.load_complexity(self.region, self.gadm_code, complexity_path.name) if add_complexity else None 
                self.buildings = gpd.read_file(buildings_path) if self.add_buildings else None 
                self.parcels = gpd.read_file(parcels_path) if self.add_parcels else None 
                self.steiner = read_steiner(steiner_path) if self.add_reblock else None 
            else:
                self.blocks = pd.concat([i_topology_utils.csv_to_geo(blocks_path), self.blocks], axis=0)
                self.complexity = pd.concat([process_worldpop.load_complexity(self.region, self.gadm_code, complexity_path.name), self.complexity], axis=0) if add_complexity else None 
                self.buildings = pd.concat([gpd.read_file(buildings_path), self.buildings], axis=0) if self.add_buildings else None 
                self.parcels = pd.concat([gpd.read_file(parcels_path), self.parcels], axis=0) if self.add_parcels else None 
                self.steiner = pd.concat([read_steiner(steiner_path), self.steiner], axis=0) if self.add_reblock else None 

        self.graph_dict = {}

        self.block_ids = self.blocks['block_id']

    @staticmethod
    def from_block_list(block_list, region, add_complexity=False, add_reblock=False, add_buildings=False, add_parcels=False):
        '''
        Allows for construction via a list of blocks rather than gadms
        '''
        gadm_list = {s[0:s.rfind("_")] for s in block_list}
        gadm_list = list(gadm_list)

        return ReblockPlotter(gadm_list=gadm_list, region=region, block_list=block_list, add_complexity=add_complexity, 
            add_reblock=add_reblock, add_buildings=add_buildings, add_parcels=add_parcels)

    def view(self, block_aois=None, add_buildings=None, add_complexity=None, add_parcels=None, save_to=None):
        
        def restrict_to_block_aois(df):
            if block_aois is None:
                return df 
            else:
                block_aoi_df = pd.DataFrame({'block_id': block_aois})
                df_sub = df.merge(block_aoi_df, how='left', on='block_id', indicator='in_aoi')
                in_aoi_bool = df_sub['in_aoi'] == 'both'
                print("overlap")
                print(in_aoi_bool.sum())
                return df_sub.loc[in_aoi_bool]


        # Allow user to override and just view without buildings
        add_buildings = self.add_buildings if add_buildings is None else add_buildings
        add_complexity = self.add_complexity if add_complexity is None else add_complexity
        #add_parcels = self.add_parcels if add_parcels is None else add_parcels

        # ax = self.blocks[self.blocks['block_id']==block_id].plot(color='black', alpha=0.2)
        if add_complexity:
            temp = restrict_to_block_aois(self.complexity)
            print(temp.shape)
            ax = temp.plot(column='complexity', legend=True, figsize=(15,15))
        else:
            temp = restrict_to_block_aois(self.blocks)
            ax = temp.plot(figsize=(15,15))

        if add_buildings:
            self.buildings.plot(color='black', alpha=0.4, ax=ax)
        if add_parcels:
            self.parcels[self.parcels['block_id']==block_id].plot(color='blue', alpha=0.4, ax=ax)

        if save_to:
            #fig = plt.gcf()
            #fig.set_size_inches
            plt.savefig(str(save_to))


    def load_block_graph(self, block_id):
        if isinstance(block_id, int):
            block_id = "{}_{}".format(self.gadm, int)

        graph_path = os.path.join(DATA, "graphs", self.region, self.gadm_code, "{}.igraph".format(block_id))
        return PlanarGraph.load_planar(graph_path)  


    def view_blocks_reblock(self, block_id, add_buildings=None, add_parcels=None, line_types='steiner'):
        '''
        Allows user to visualize reblocking for a single specified block, as determined by the block_id
        Note, if you've imported building and parcels when constructing the viewer, you can choose
        to include/not include them when viewing
        '''
        
        if isinstance(block_id, int):
            block_id = "{}_{}".format(self.gadm, int)

        # Allow user to override and just view without buildings
        add_buildings = self.add_buildings if add_buildings is None else add_buildings
        add_parcels = self.add_parcels if add_parcels is None else add_parcels

        ax = self.blocks[self.blocks['block_id']==block_id].plot(color='black', alpha=0.2)
        self.terminal[self.terminal['block_id']==block_id].plot(color='red', ax=ax)

        if line_types == 'steiner':
            self.steiner[self.steiner['block_id']==block_id].plot(color='red', ax=ax)
        elif line_types == 'all':
            self.graph_dict['block_id'] = self.load_block_graph(block_id)
            lines = convert_to_lines(self.graph_dict['block_id'])
            lines_geo = gpd.GeoSeries(lines)
            lines_geo.plot(color='red', ax=ax)

        if add_buildings:
            self.buildings.plot(color='blue', alpha=0.4, ax=ax)
        if add_parcels:
            self.parcels[self.parcels['block_id']==block_id].plot(color='blue', alpha=0.4, ax=ax)


    def view_all_reblock(self, add_buildings=None, add_parcels=None):
        '''
        Calling this will visualize the reblocking for the entire area you've specified in your constructor
        '''

        # Allow user to override and just view without buildings
        add_buildings = self.add_buildings if add_buildings is None else add_buildings
        add_parcels = self.add_parcels if add_parcels is None else add_parcels

        ax = self.blocks.plot(color='black', alpha=0.2)
        self.steiner.plot(color='red', ax=ax)
        #self.terminal.plot(color='red', ax=ax)
        if add_buildings:
            self.buildings.plot(color='blue', alpha=0.4, ax=ax)

        if add_parcels:
            self.parcels.plot(color='blue', alpha=0.4, ax=ax)

    def export_parcels(self, output_filename):
        self.parcels.to_file(output_filename, driver='GeoJSON')

    def export_steiner(self, output_filename):

        fail_bool = self.steiner['geometry'].isna()
        steiner_fails = self.steiner[fail_bool]
        steiner_success = self.steiner[~fail_bool]
        self.steiner_success.to_file(output_filename, driver='GeoJSON')

#from bokeh_view import *
aoi_paths = DATA /"LandScan_Global_2018" / "aoi_datasets"

# known_slum_df = pd.read_csv("../Monrovia_Freetown_Kibera.csv")

# # (1) Kibera
nairobi_path = [p for p in aoi_paths.iterdir() if "nair" in str(p)][0] 
nairobi = ComplexityViewer(region='Africa', aoi_path=nairobi_path) 
# kibera_df = nairobi.restrict(gadm_aois=gadm_list)
# #aoi_analysis.make_box_plot_summary(kibera_df, "Kibera, Nairobi", outpath="./bokeh/kibera_plot.png")
# make_bokeh(kibera_df, "./bokeh/kibera_bokeh.html")

# # (2) Monrovia -- LBR
# known_monrovia = list(known_slum_df[known_slum_df['country_code']=='LBR']['block_id'])
# monrovia_path = [p for p in aoi_paths.iterdir() if "monrovia" in str(p)][0] 
# monrovia = ComplexityViewer(region='Africa', aoi_path=monrovia_path) 
# monrovia_slum_df = monrovia.restrict(block_aois=known_monrovia)
# #aoi_analysis.make_box_plot_summary(monrovia_slum_df, "Monrovia slums", outpath="./bokeh/monrovia_slum_plot.png")
# make_bokeh(monrovia_slum_df, "./bokeh/monrovia_slum_bokeh.html")

# # (3) Port au prince -- HTI
# known_portauprince = list(known_slum_df[known_slum_df['country_code']=='HTI']['block_id'])
# portauprince_path = [p for p in aoi_paths.iterdir() if "prince" in str(p)][0] 
# portauprince = ComplexityViewer(region='Africa', aoi_path=portauprince_path) 
# portauprince_slum_df = portauprince.restrict(block_aois=known_portauprince)
# #aoi_analysis.make_box_plot_summary(portauprince_slum_df, "Port au Prince", outpath="./bokeh/port_au_prince_slum_plot.png")
# make_bokeh(portauprince_slum_df, "./bokeh/port_au_prince_slum_bokeh.html")

# # (4) Freetown -- SLE
# freetown_path = [p for p in aoi_paths.iterdir() if "free" in str(p)][0] 
# freetown = ComplexityViewer(region='Africa', aoi_path=freetown_path) 
# freetown_df = freetown.restrict(gadm_aois=['SLE.4.2.1_1'])
# #aoi_analysis.make_box_plot_summary(freetown_df, "Freetown, SL", outpath="./bokeh/freetown_slum_plot.png")
# make_bokeh(freetown_df, "./bokeh/freetown_bokeh.html")

import statsmodels.api as sm 
from mpl_toolkits import mplot3d
from statsmodels.nonparametric.kde import kernel_switch
cols = ['complexity', 'bldg_density']
data = nairobi.complexity[cols]
missing_compl = data['complexity'].isna()
data = data.loc[~missing_compl]

x = data['complexity'].values
y = data['bldg_density'].values 
#y = np.log(y)
bandwidth = 0.1
dens_fn = sm.nonparametric.KDEMultivariate(data=[x, y], var_type='oc', bw=[bandwidth, bandwidth])

x_min = 5
x_max = x.max()
y_min = 0.0
y_max = 1.0

x_plot_point_count = 20 
y_plot_point_count = 40
x_plot_vals = np.linspace(x_min, x_max, x_plot_point_count) 
y_plot_vals = np.linspace(y_min, y_max, y_plot_point_count) 
X_plot, Y_plot = np.meshgrid(x_plot_vals, y_plot_vals)
eval_data = [X_plot.ravel(), Y_plot.ravel()]
z = dens_fn.pdf(eval_data)
Z_plot = z.reshape(X_plot.shape)

ax = plt.axes(projection='3d')  
ax.plot_surface(X_plot, Y_plot, Z_plot, cmap='viridis') 

# if __name__ == "__main__":
#     # gadm_list = ['KEN.30.10.1_1',
#     #  'KEN.30.10.2_1',
#     #  'KEN.30.10.3_1',
#     #  'KEN.30.10.4_1',
#     #  'KEN.30.10.5_1',
#     #  'KEN.30.11.2_1']
#     # gadm_list = ['LBR.11.2.1_1']
#     # #gadm_list = ['DJI.2.1_1']
#     # region = 'Africa'
#     # #viewer = ReblockPlotter(gadm_list, region, add_parcels=False, add_buildings=True)

#     # viewer = ReblockPlotter(gadm_list, region, add_parcels=False, add_buildings=False)
#     # viewer.export_steiner(REBLOCK_VIEWIING / "{}_parcels.geojson".format(gadm_list[0]))

#     gadm_list = ['SLE.4.2.1_1']
#     region = 'Africa'
#     viewer = ReblockPlotter(gadm_list, region, add_parcels=False, add_buildings=False)
#     viewer.export_steiner(REBLOCK_VIEWIING / "{}_opt_path.geojson".format(gadm_list[0]))

    # # This will allow you to view the optimal paths
    # # viewer.view_all()
    # # plt.show()

    # # Now we export to files, assuming we've sanity checked the output and it looks good
    # viewer.export_parcels(os.path.join(DATA, 'KEN_parcels.geojson'))
    # viewer.export_steiner(os.path.join(DATA, 'KEN_opt_path.geojson'))


