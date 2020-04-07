import numpy as np 
#import rasterio 
#import rasterio.features
from pathlib import Path 
import geopandas as gpd 
import pandas as pd 
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.wkt import loads
import argparse 
import tqdm
import copy 
#import requests
import json
import ast 
from functools import reduce
import operator
import matplotlib.pyplot as plt 

root = Path('../')
DATA = root / 'data' 
COMPLEXITY = DATA / "complexity"
BLOCKS = DATA / "blocks"
BUILDINGS = DATA / "buildings"
GADM = DATA / "GADM"
AOI_TRACKER = DATA / 'LandScan_Global_2018' / "aoi_tracker.csv" 
CITY_BOUNDARIES = DATA / 'city_boundaries'

possibilities = [u'seaborn-darkgrid', u'seaborn-notebook', u'classic', u'seaborn-ticks', u'grayscale', u'bmh', u'seaborn-talk', u'dark_background', u'ggplot', u'fivethirtyeight', u'_classic_test', u'seaborn-colorblind', u'seaborn-deep', u'seaborn-whitegrid', u'seaborn-bright', u'seaborn-poster', u'seaborn-muted', u'seaborn-paper', u'seaborn-white', u'seaborn-pastel', u'seaborn-dark', u'seaborn', u'seaborn-dark-palette']
style_str = ['seaborn-whitegrid']
plt.style.use(style_str)

# region_mapper = {
#     'greater_monrovia': 'Africa',
#     'nairobi': 'Africa',
#     'douala': 'Africa',
#     'kinshasa': 'Africa',
#     'blantyre': 'Africa',
#     'port_au_prince': 'Central-America',
#     'caracas': 'South-America',
#     'kathmandu': 'Asia',
#     'freetown': 'Africa'
# }

# title_mapper = {
#     'greater_monrovia': 'Block complexity summary - Greater Monrovia',
#     'nairobi': 'Block complexity summary - Nairobi',
#     'douala': 'Block complexity summary - Douala',
#     'kinshasa': 'Block complexity summary - Kinshasa',
#     'blantyre': 'Block complexity summary - Blantyre',
#     'port_au_prince': 'Block complexity summary - Port au Prince',
#     'caracas': 'Block complexity summary - Caracas',
#     'kathmandu': 'Block complexity summary - Kathmandu',
#     'freetown': 'Block complexity summary - Freetown'

# }

def complexity_bar_chart(ax, hist_params, x_label, y_label, title ):

    #bar_chart = plt.bar(**hist_params)
    height_total = round(hist_params['height'].sum())
    ax.bar(**hist_params)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title+"\ntotal={}".format(height_total))
    ax.set_xlim(left=0)
    # plt.xlabel(x_label)
    # plt.ylabel(y_label)
    # plt.title(title)
    #plt.show()

#plt.bar(x_compl, y_height, width=1.0, linewidth=.5, edgecolor='black')

def make_hist_summary(df, main_title, outpath=None):

    # Load our geodataframe
    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geometry'].apply(loads)
    is_neg_pop = gdf['pop_est'] < 0
    print("There are {} neg pop".format(is_neg_pop.sum()))
    gdf.loc[(is_neg_pop), 'pop_est'] = 0


    fns = {'block_id': 'count', 
          'bldg_count': 'sum', 
          'total_bldg_area_sq_km': 'sum', 
          'block_area_km2': 'sum', 
          'pop_est': 'sum'} 
    gb = gdf.groupby('complexity').agg(fns) 


    fig, axes = plt.subplots(nrows=3, ncols=2)
    fig.tight_layout(pad=1.5)
    fig.set_size_inches((12, 16))
    fig.suptitle(main_title)

    fig_params = {'block_id': {'x_label': 'Block complexity',
                               'y_label': 'Total block count',
                               'title': 'Block count by complexity'},
                  'bldg_count': {'x_label': 'Block complexity',
                               'y_label': 'Total building count',
                               'title': 'Building count by complexity'},
                  'total_bldg_area_sq_km': {'x_label': 'Block complexity',
                               'y_label': 'Total building area (sq km)',
                               'title': 'Building area by complexity'},
                  'block_area_km2': {'x_label': 'Block complexity',
                               'y_label': 'Total block area (sq km)',
                               'title': 'Block area by complexity'},
                  'pop_est': {'x_label': 'Block complexity',
                               'y_label': 'Total estimated population',
                               'title': 'Population est. by complexity'}
                                                              }
    subplot_coords = {'block_id': (0,0), 
                      'block_area_km2': (0,1),
                      'bldg_count': (1,0),
                      'total_bldg_area_sq_km': (1,1),
                      'pop_est': (2,0)}

    for c in gb.columns:
        hist_params = {'x': gb.index.values,
                       'width': 1.0,
                       'height':gb[c].values}
        f = fig_params[c]
        cur_ax = axes[subplot_coords[c]]
        # print(f)
        # print(hist_params)
        # print(cur_ax)
        complexity_bar_chart(cur_ax, hist_params, **f)
    #gdf.plot(column='complexity', ax=axes[(2,1)])

    gdf.plot(column='complexity', ax=axes[(2,1)], cmap='Reds')
    if outpath is not None:
        plt.savefig(outpath)

def get_aoi(f):
    s = str(f.stem).replace("analysis_","")
    return s

def make_histograms_all_aoi():

    p = Path('../data/LandScan_Global_2018/aoi_datasets/')
    aoi_files_temp = list(p.iterdir())
    aoi_files = [x for x in aoi_files_temp]

    for aoi_file in aoi_files:
        aoi = get_aoi(aoi_file)
        print("Processing {}".format(aoi))

        main_title = title_mapper[aoi]
        outpath = Path("./hist_summaries/{}.png".format(aoi))
        outpath.parent.mkdir(exist_ok=True, parents=True)
        df = pd.read_csv(str(aoi_file))

        make_hist_summary(df, main_title, outpath)


#make_histograms_all_aoi()


def make_box_plot_column(df, col, ax, title, x_label, y_label):
    #print("col = {}".format(col))
    #print("ax = {}".format(ax))

    gb = df[['complexity', col]].groupby('complexity')
    x = df['complexity'].values
    y = df[col].values
    corr_mat = np.corrcoef(x,y)
    coef = corr_mat[0,1]
    title = "{} \n corr. = {}".format(title, coef)

    data_list = [gb.get_group(k)[col].values for k in gb.groups.keys() ]
    labels = list(gb.groups.keys())

    ax.boxplot(x=data_list, labels=labels)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.set_xlim(left=0)

box_plot_cols = ['block_area_km2', 'bldg_count', 'total_bldg_area_sq_km',
                 'bldg_density', 'pop_est']


def prep_df(df):
    '''
    Just a tiny function to convert a df to GeoDF and calculate
    the building density
    '''
    gdf = gpd.GeoDataFrame(df)
    gdf['geometry'] = gdf['geometry'].apply(loads)
    is_neg_pop = gdf['pop_est'] < 0
    print("There are {} neg pop".format(is_neg_pop.sum()))
    print()
    gdf.loc[(is_neg_pop), 'pop_est'] = 0
    gdf['bldg_density'] = gdf['total_bldg_area_sq_km'] / gdf['block_area_km2']
    gt1 = gdf['bldg_density'] > 1
    print("There are {} gt 1".format(gt1.sum()))
    gdf = gdf.loc[~gt1]
    return gdf 

def make_series_for_xcountry(df):

    # Prepare the geo dataframe
    gdf = prep_df(df)
    cols = ['complexity'] + box_plot_cols
    gb_mean = gdf[cols].groupby('complexity').mean()
    gb_median = gdf[cols].groupby('complexity').median()
    return gb_mean, gb_median


def make_box_plot_summary(df, main_title, outpath=None):

    # Prepare the geo dataframe
    gdf = prep_df(df)
    # gdf = gpd.GeoDataFrame(df)
    # gdf['geometry'] = gdf['geometry'].apply(loads)
    # is_neg_pop = gdf['pop_est'] < 0
    # print("There are {} neg pop".format(is_neg_pop.sum()))
    # print()
    # gdf.loc[(is_neg_pop), 'pop_est'] = 0
    # gdf['bldg_density'] = gdf['total_bldg_area_sq_km'] / gdf['block_area_km2']

    # Make the subplots
    fig, axes = plt.subplots(nrows=3, ncols=2)
    fig.tight_layout(pad=1.5)
    fig.set_size_inches((12, 16))
    fig.suptitle(main_title)

    # box_plot_cols = ['block_area_km2', 'bldg_count', 'total_bldg_area_sq_km',
    #              'bldg_density', 'pop_est']
    # box_plot_cols = ['bldg_count', 'total_bldg_area_sq_km',
    #              'bldg_density', 'pop_est']

    subplot_coords = { 'bldg_density':(0,0),
                      'block_area_km2': (0,1),
                      'bldg_count': (1,0),
                      'total_bldg_area_sq_km': (1,1),
                      'pop_est': (2,0)}

    fig_params = {'bldg_density': {'x_label': 'Block complexity',
                               'y_label': 'Building density within a block',
                               'title': 'Building area / block area'},
                  'bldg_count': {'x_label': 'Block complexity',
                               'y_label': 'Building count within a block',
                               'title': 'Building count by complexity'},
                  'total_bldg_area_sq_km': {'x_label': 'Block complexity',
                               'y_label': 'Building area (sq km)',
                               'title': 'Building area by complexity'},
                  'block_area_km2': {'x_label': 'Block complexity',
                               'y_label': 'Block area (sq km)',
                               'title': 'Block area by complexity'},
                  'pop_est': {'x_label': 'Block complexity',
                               'y_label': 'Estimated population by block',
                               'title': 'Population est. by complexity'}
                                                              }

    for col in box_plot_cols:
        # print("Column test == {}".format(col))
        # print("coords are == {}".format(subplot_coords[col]))
        cur_ax = axes[subplot_coords[col]]
        title = fig_params[col]['title']
        x_label = fig_params[col]['x_label']
        y_label = fig_params[col]['y_label']
        make_box_plot_column(gdf, col, cur_ax, title, x_label, y_label)
        #plt.show()

    if outpath is not None:
        plt.savefig(outpath)

# boxplot_title_mapper = {
#     'greater_monrovia': 'Box-plot block complexity summary - Greater Monrovia',
#     'nairobi': 'Box-plot block complexity summary - Nairobi',
#     'douala': 'Box-plot block complexity summary - Douala',
#     'kinshasa': 'Box-plot block complexity summary - Kinshasa',
#     'blantyre': 'Box-plot block complexity summary - Blantyre',
#     'port_au_prince': 'Box-plot block complexity summary - Port au Prince',
#     'caracas': 'Box-plot block complexity summary - Caracas',
#     'kathmandu': 'Box-plot block complexity summary - Kathmandu',
#     'freetown': 'Box-plot block complexity summary - Freetown',
  
# }

def make_boxplots_all_aoi():

    p = Path('../data/LandScan_Global_2018/aoi_datasets/')
    aoi_files_temp = list(p.iterdir())
    aoi_files = [x for x in aoi_files_temp if "freetown" in str(x)]

    for aoi_file in aoi_files:
        aoi = get_aoi(aoi_file)
        print("Processing {}".format(aoi))

        main_title = boxplot_title_mapper[aoi]
        outpath = Path("./boxplot_summaries/{}.png".format(aoi))
        outpath.parent.mkdir(exist_ok=True, parents=True)
        df = pd.read_csv(str(aoi_file))

        make_box_plot_summary(df, main_title, outpath)

def get_aoi_dataset_path(aoi_name):
    p = DATA / 'LandScan_Global_2018' / 'aoi_datasets'
    pt = p / "analysis_{}.csv".format(aoi_name)
    return pt 

def make_plots_for_aoi(aoi_df, aoi_description, update=False):
  '''
  Make histogram and box plots for all AoI's included 
  in some csv file and then make a cross-country summary
  as well
  '''
  aoi_df = aoi_df.loc[aoi_df['wkt_url'] != "not_available"]
  gb_mean_concat = []
  gb_median_concat = []

  for i, obs in aoi_df.iterrows():
    region = obs['region']
    aoi_name = obs['aoi_name']
    city = obs['city']
    country_code = obs['country_code']

    # Get path to aoi dataset
    aoi_path = get_aoi_dataset_path(aoi_name)
    assert aoi_path.is_file(), "Aoi file at {} does not exist".format(aoi_path)
    
    # (1) Make histograms
    aoi_data = pd.read_csv(aoi_path)
    outpath = Path("./hist_summaries/{}.png".format(aoi_name))
    outpath.parent.mkdir(exist_ok=True, parents=True)    
    main_title = "Block complexity summary - {}".format(city)
    if not outpath.is_file() or update:
      make_hist_summary(aoi_data, main_title, outpath)

    # (2) Make boxplots
    aoi_data = pd.read_csv(aoi_path)
    outpath = Path("./boxplot_summaries/{}.png".format(aoi_name))
    outpath.parent.mkdir(exist_ok=True, parents=True)    
    main_title = "Box plot block complexity summary - {}".format(city)
    if not outpath.is_file() or update:
      make_box_plot_summary(aoi_data, main_title, outpath)

    # (3) Make figs for cross-country comparison
    aoi_data = pd.read_csv(aoi_path)
    gb_mean, gb_median = make_series_for_xcountry(aoi_data)
    gb_mean['city'] = city 
    gb_median['city'] = city 
    gb_mean_concat.append(gb_mean)
    gb_median_concat.append(gb_median)

  all_mean = pd.concat(gb_mean_concat).reset_index()
  outpath = Path("./cross_country/{}.png".format(aoi_description+" - Mean"))
  outpath.parent.mkdir(exist_ok=True, parents=True)      
  plot_cross_country(all_mean, aoi_description+" - Mean", outpath)

  all_median = pd.concat(gb_median_concat).reset_index()
  outpath = Path("./cross_country/{}.png".format(aoi_description+" - Median"))
  outpath.parent.mkdir(exist_ok=True, parents=True)      
  plot_cross_country(all_median, aoi_description+" - Median", outpath)

def plot_cross_country(df, main_title, outpath):
    fig, axes = plt.subplots(nrows=3, ncols=2)
    fig.tight_layout(pad=1.5)
    fig.set_size_inches((12, 16))
    fig.suptitle(main_title)

    # box_plot_cols = ['block_area_km2', 'bldg_count', 'total_bldg_area_sq_km',
    #              'bldg_density', 'pop_est']
    # box_plot_cols = ['bldg_count', 'total_bldg_area_sq_km',
    #              'bldg_density', 'pop_est']

    subplot_coords = { 'bldg_density':(0,0),
                      'block_area_km2': (0,1),
                      'bldg_count': (1,0),
                      'total_bldg_area_sq_km': (1,1),
                      'pop_est': (2,0)}

    fig_params = {'bldg_density': {'x_label': 'Block complexity',
                               'y_label': 'Building density within a block',
                               'title': 'Building area / block area'},
                  'bldg_count': {'x_label': 'Block complexity',
                               'y_label': 'Building count within a block',
                               'title': 'Building count by complexity'},
                  'total_bldg_area_sq_km': {'x_label': 'Block complexity',
                               'y_label': 'Building area (sq km)',
                               'title': 'Building area by complexity'},
                  'block_area_km2': {'x_label': 'Block complexity',
                               'y_label': 'Block area (sq km)',
                               'title': 'Block area by complexity'},
                  'pop_est': {'x_label': 'Block complexity',
                               'y_label': 'Estimated population by block',
                               'title': 'Population est. by complexity'}
                                                              }
    box_plot_cols = ['block_area_km2', 'bldg_count', 'total_bldg_area_sq_km',
                 'bldg_density', 'pop_est']

    for i, col in enumerate(box_plot_cols):
        # print("Column test == {}".format(col))
        # print("coords are == {}".format(subplot_coords[col]))
        cur_ax = axes[subplot_coords[col]]
        title = fig_params[col]['title']
        x_label = fig_params[col]['x_label']
        y_label = fig_params[col]['y_label']
        make_line_plot_column(df, col, cur_ax, title, x_label, y_label)

        if i == 0:
          cur_ax.legend(loc='lower right')
    plt.savefig(outpath)

def make_line_plot_column(gdf, col, cur_ax, title, x_label, y_label):
    
    cities = gdf['city'].unique()
    for city in cities:
      cur_x = gdf[gdf['city']==city]['complexity'].values
      cur_y = gdf[gdf['city']==city][col].values  
      cur_ax.plot(cur_x, cur_y, label=city)
    cur_ax.set_xlabel(x_label)
    cur_ax.set_ylabel(y_label)
    cur_ax.set_title(title)
    cur_ax.set_xlim(left=0)



#make_boxplots_all_aoi()
# p = Path('../data/LandScan_Global_2018/aoi_datasets/')
# aoi_files = list(p.iterdir())
# df = pd.read_csv(aoi_files[0]) 

# make_box_plot_summary(df,main_title='test of main title')

# def join_with_reblock():

# import geopandas as gpd
# import pandas as pd 
# from pathlib import Path 

# root = Path('../')
# DATA = root / 'data' 
# aoi_file = DATA / 'LandScan_Global_2018' / 'aoi_datasets' / 'analysis_freetown.csv'
# #reblock_file = DATA / 'reblock' / 'Africa' / 'SLE' / 'steiner_lines_SLE.4.2.1_1.csv'
# reblock_file = DATA / 'reblock_viewing' / 'SLE.4.2.1_1_opt_path.geojson'

# aoi = pd.read_csv(str(aoi_file))
# reblock = gpd.read_file(str(reblock_file))
# #reblock['geometry'] = reblock['geometry'].apply(loads)
# reblock['len'] = reblock['geometry'].to_crs({'init': 'epsg:3395'}).length / (10**3)
# reblock.rename(columns={'block': 'block_id'}, inplace=True)
# block_len = reblock[['len', 'block_id', 'line_type']]
# block_len_long = block_len.pivot(index='block_id', columns='line_type', values='len')
# block_len_long.reset_index(inplace=True)
# block_len_long.rename(columns={'existing_steiner': 'existing', 'new_steiner': 'new'}, inplace=True)

# merged = pd.merge(aoi, block_len_long, on='block_id')


