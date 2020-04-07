import numpy as np 
import rasterio 
import rasterio.features
from pathlib import Path 
import geopandas as gpd 
import pandas as pd 
from shapely.geometry import MultiPolygon, Polygon, MultiLineString
from shapely.wkt import loads
import argparse 
import tqdm
import copy 
import requests
import json
import ast 
from functools import reduce
import operator

root = Path('../')
DATA = root / 'data' 
COMPLEXITY = DATA / "complexity"
BLOCKS = DATA / "blocks"
BUILDINGS = DATA / "buildings"
GADM = DATA / "GADM"
AOI_TRACKER = DATA / 'LandScan_Global_2018' / "aoi_tracker.csv" 

mapper = {
    'greater_monrovia': 'Africa',
    'nairobi': 'Africa',
    'douala': 'Africa',
    'kinshasa': 'Africa',
    'blantyre': 'Africa',
    'port_au_prince': 'Central-America',
    'caracas': 'South-America',
    'kathmandu': 'Asia'
}

def make_aoi_dataset():
    aoi_tracker = pd.read_csv(AOI_TRACKER)
    convert_fn = lambda x: ast.literal_eval(x)
    aoi_tracker['gadm_list'] = aoi_tracker['gadm_list'].apply(convert_fn) 
    aoi_tracker['block_list'] = aoi_tracker['block_list'].apply(convert_fn) 

    for i, row in aoi_tracker.iterrows():
        gadm_list = row['gadm_list']
        block_list = row['block_list']
        aoi_name = row['aoi_name']
        region = mapper[aoi_name]
        complexity_pop = assemble_complexity_pop(region, gadm_list, block_list)
        complexity_pop['geometry'] = complexity_pop['geometry'].apply(lambda x: x.wkt)
        p = DATA / 'LandScan_Global_2018' / 'aoi_datasets'
        p.mkdir(parents=True, exist_ok=True)
        complexity_pop.to_csv(str(p / "analysis_{}.csv".format(aoi_name)), index=False)


def assemble_complexity_pop(region, gadm_list, block_list):
    '''
    Given a list of gadms and blocks, assemble the complexity pop
    files and return 
    '''
    if isinstance(gadm_list, str):
        gadm_list = ast.literal_eval(gadm_list)
    if isinstance(block_list, str):
        block_list = ast.literal_eval(block_list)

    # Load all gadm's
    country_code = gadm_list[0].split(".")[0]
    p = DATA / 'LandScan_Global_2018' / region / country_code  
    gadm_paths = [p / "complexity_pop_{}.csv".format(g) for g in gadm_list]
    complexity_pop = pd.concat([pd.read_csv(p) for p in gadm_paths if p.is_file()])
    complexity_pop = gpd.GeoDataFrame(complexity_pop)
    complexity_pop['geometry'] = complexity_pop['geometry'].apply(loads)
    complexity_pop.geometry.crs = {'init': 'epsg:4326'}  
    complexity_pop.crs = {'init': 'epsg:4326'}

    # Now limit to only our blocks
    aoi_blocks_df = pd.DataFrame.from_dict({'block_id':block_list})
    complexity_pop = complexity_pop.merge(aoi_blocks_df, how='left', indicator=True)
    complexity_pop = complexity_pop[complexity_pop['_merge']=="both"]

    return complexity_pop



def load_complexity_pop(region, country_code, gadm):
    landscan_path = DATA / 'LandScan_Global_2018' / region / country_code
    complexity_pop_path = landscan_path / "complexity_pop_{}.csv".format(gadm) 
    gdf = gpd.GeoDataFrame(pd.read_csv(complexity_pop_path))
    gdf['geometry'] = gdf['geometry'].apply(loads)
    gdf.geometry.crs = {'init': 'epsg:4326'}  
    gdf.crs = {'init': 'epsg:4326'}
    #gdf.drop(columns=['Unnamed: 0'], inplace=True)
    return gdf 

def get_gadm_from_file(f):
    gadm = f.replace(".csv", "").replace("blocks_", "").replace("complexity_", "")
    gadm = gadm.replace(".geojson", "")
    return gadm 

def join_with_buildings(gdf, region, country_code, gadm):

    bldg_path = BUILDINGS / region / country_code / "buildings_{}.geojson".format(gadm)
    bldg_gdf = gpd.read_file(bldg_path)
    bldg_gdf = bldg_gdf[['osm_id', 'geometry']]
    joined = gpd.sjoin(gdf, bldg_gdf, how='left')
    joined = joined.merge(bldg_gdf, how='left', on='osm_id', suffixes=["", "_bldgs"])

    # Make a temp series so we can calculate the area of each building
    missing = joined['geometry_bldgs'].isna().sum()
    if missing > 0:
        print("NOTE: there are {} missing geoms".format(missing))
        joined['geometry_bldgs'] = joined['geometry_bldgs'].fillna(Polygon([]))
    geo_series = gpd.GeoSeries(joined['geometry_bldgs'])
    geo_series.crs = {'init': 'epsg:4326'}
    joined['bldg_area_sq_km'] = geo_series.to_crs({'init': 'epsg:3395'}).area / (10**6)  

    bldgs_by_block = joined[['block_id', 'geometry_bldgs', 'bldg_area_sq_km']].groupby('block_id').aggregate(list)
    bldgs_by_block.reset_index(inplace=True)
    gdf_w_buildings = gdf.merge(bldgs_by_block, how='left', on='block_id')
    gdf_w_buildings['geometry_bldgs'] = gdf_w_buildings['geometry_bldgs'].map(lambda x_list: [x.wkt for x in x_list])
    
    # Area of each building is stored in a list, so sum it
    sum_fn = lambda area_list : reduce(operator.add, area_list)
    gdf_w_buildings['total_bldg_area_sq_km'] = gdf_w_buildings['bldg_area_sq_km'].map(sum_fn)

    return gdf_w_buildings 

def load_block(region,country_code, f):
    p = BLOCKS / region / country_code / f
    gadm = get_gadm_from_file(f)
    df = pd.read_csv(p)
    df.drop(columns=['Unnamed: 0'], inplace=True)
    #gdf_complexity = gpd.GeoDataFrame(df[['block_id', 'geometry', 'complexity', 'centroids_multipoint']])
    gdf_block = gpd.GeoDataFrame(df[['block_id', 'geometry']])
    gdf_block['complexity'] = None #float("NaN")
    gdf_block['centroids_multipoint'] = None #float("NaN")
    gdf_block['geometry'] = gdf_block['geometry'].apply(loads)
    gdf_block.geometry.crs = {'init': 'epsg:4326'}  
    gdf_block.crs = {'init': 'epsg:4326'}  
    gdf_block['bldg_count'] = 0
    
    gdf_block['block_area_km2'] = gdf_block['geometry'].to_crs({'init': 'epsg:3395'}).area / (10**6)  
    #gdf_block = join_with_buildings(gdf_block, region, country_code, gadm)

    return gdf_block

def load_complexity(region, country_code, f):
    '''
    Load the complexity file. Note, if the file does not exist then
    just return None
    '''

    p = COMPLEXITY / region / country_code / f
    block_f = f.replace("complexity_", "blocks_")
    block_p = BLOCKS / region / country_code / block_f
    if p.is_file():
        gadm = get_gadm_from_file(f)

        df = pd.read_csv(p)
        gdf_complexity = gpd.GeoDataFrame(df[['block_id', 'geometry', 'complexity', 'centroids_multipoint']])
        gdf_complexity['geometry'] = gdf_complexity['geometry'].apply(loads)
        gdf_complexity.geometry.crs = {'init': 'epsg:4326'}  
        gdf_complexity.crs = {'init': 'epsg:4326'}  
        gdf_complexity['centroids_multipoint'] = gdf_complexity['centroids_multipoint'].apply(loads)
        gdf_complexity['bldg_count'] = gdf_complexity['centroids_multipoint'].apply(lambda x: len(x))
        
        gdf_complexity['block_area_km2'] = gdf_complexity['geometry'].to_crs({'init': 'epsg:3395'}).area / (10**6)  
        gdf_complexity = join_with_buildings(gdf_complexity, region, country_code, gadm)


    elif block_p.is_file():
        print("Complexity file does not exist: {}".format(str(p)))
        print("Loading from the block file")
        #block_f = f.replace("complexity_", "blocks_")
        gdf_complexity = load_block(region, country_code, block_f)
    else:
        print("\n\n Complexity and block files do not exist: {}\n{}".format(str(p), str(block_p)))
        return None 

    return gdf_complexity
    # gadm = get_gadm_from_file(f)

    # df = pd.read_csv(p)
    # gdf_complexity = gpd.GeoDataFrame(df[['block_id', 'geometry', 'complexity', 'centroids_multipoint']])
    # gdf_complexity['geometry'] = gdf_complexity['geometry'].apply(loads)
    # gdf_complexity.geometry.crs = {'init': 'epsg:4326'}  
    # gdf_complexity.crs = {'init': 'epsg:4326'}  
    # gdf_complexity['centroids_multipoint'] = gdf_complexity['centroids_multipoint'].apply(loads)
    # gdf_complexity['bldg_count'] = gdf_complexity['centroids_multipoint'].apply(lambda x: len(x))
    
    # gdf_complexity['block_area_km2'] = gdf_complexity['geometry'].to_crs({'init': 'epsg:3395'}).area / (10**6)  
    # gdf_complexity = join_with_buildings(gdf_complexity, region, country_code, gadm)

    # return gdf_complexity

def add_landscan_data(ls_dataset, gdf_complexity):

    fn = lambda x: rasterio.features.geometry_window(ls_dataset, [x])
    gdf_complexity['windows'] = gdf_complexity['geometry'].apply(fn)

    return gdf_complexity 

def calculate_population_uniform_dist(geom, ls_dataset, window):
    '''
    '''

    data = ls_dataset.read(1, window=window)
    trans = ls_dataset.window_transform(window)

    geo_series = []
    pop_series = []
    for shape, pop in rasterio.features.shapes(data, transform=trans):
        geo_series.append(Polygon(shape['coordinates'][0]))
        assert shape['type'] == 'Polygon', "ERROR -- not Polygon"
        pop_series.append(pop)
    geo_series = gpd.GeoSeries(geo_series)
    
    #print("\n\ntest ")
    geo_series_valid = geo_series.is_valid
    geom_valid = geom.is_valid
    #print("geo_series {}".format(np.all(geom_valid)))
    #print(type(geom))
    #print("geom {}".format(geom.is_valid))
    #print("geo_series")
    try:
        temp_geom = geo_series.intersection(geom)
    except:
        geo_series = geo_series.buffer(0)
        temp_geom = geo_series.intersection(geom)

    #print("temp_geom {}".format(np.all(temp_geom.is_valid)))
    inter_pct = temp_geom.area / geo_series.area
    #inter_pct = geo_series.intersection(geom).area / geo_series.area 
    #print("through intersection")

    avg_pop = (inter_pct.values * np.array(pop_series)).sum()

    #return geo_series, pop_series 
    return avg_pop

def process_gadm_landscan(region, country_code, gadm):

    # region = 'Africa'
    # country_code = 'DJI'
    # country_code = 'SLE'
    # gadm = 'SLE.4.2.1_1'
    # gadm = 'DJI.1.1_1'
    landscan_path = DATA / 'LandScan_Global_2018' / 'raw_tif' / 'ls_2018.tif'

    ls_dataset = rasterio.open(landscan_path)
    f = "complexity_{}.csv".format(gadm)

    # Load the complexity file
    gdf_complexity = load_complexity(region, country_code, f)
    if gdf_complexity is None:
        print("FAILURE - Could not find block or complexity files for {}-{}-{}".format(region, country_code, gadm))
        return False 

    # Add the landscan window for each block's geometry
    gdf_complexity = add_landscan_data(ls_dataset, gdf_complexity)

    # Now calculate the pop estimate for each block
    pop_fn = lambda s: calculate_population_uniform_dist(s['geometry'], ls_dataset, s['windows'])
    gdf_complexity['pop_est'] = gdf_complexity.apply(pop_fn, axis=1)
    gdf_complexity['windows'] = gdf_complexity['windows'].map(lambda x: x.todict())
    gdf_complexity['geometry'] = gdf_complexity['geometry'].map(lambda x: x.wkt)
    

    f = "complexity_pop_{}.csv".format(gadm)
    output_path = DATA / 'LandScan_Global_2018' / region / country_code
    output_path.mkdir(parents=True, exist_ok=True)
    #gdf_complexity.to_file(output_path / f, driver='GeoJSON')
    gdf_complexity.to_csv(output_path / f, index=False)

    return True

def process_path_landscan(path_to_complexity_files):

    p = Path(path_to_complexity_files)
    country_code = p.stem 
    region = p.parent.stem
    all_files = list(p.iterdir())
    for full_path in tqdm.tqdm(all_files, total=len(all_files)):
        gadm = full_path.stem.replace('complexity_', '')
        process_gadm_landscan(region, country_code, gadm)

def get_gadm_level(country_code):   

    # Tiny helper to extract the int level from a gadm file path
    get_int = lambda f: int(f.stem[-1])

    # These are all the shape files in the dir
    shp_files = [f for f in (GADM / country_code).iterdir() if "shp" in str(f)]

    # Now sort via the final digit, which indicates the level
    shp_files.sort(key=get_int)

    # Return the largest level
    return get_int(shp_files[-1])


def AoI_intersects_with_gadms(aoi_geom, country_code):
    '''
    Given an area of interest and a 3-letter country code, this determines
    which GADM's that area intersects with. This is a helper function in 
    generating summary stats for that area.

    Inputs:
        - aoi_geom (Polygon) shapely polygon defining Area of Interest
        - country_code (str) 3-letter country code 
    Outputs:
        - intersected_gadms (List[str]) list of gadm's that intersect with AoI
    '''

    # The level of nesting of gadm's varies from country to country
    gadm_depth = get_gadm_level(country_code)
    gadm_path = GADM / country_code / "gadm36_{}_{}.shp".format(country_code, gadm_depth)
    gadm = gpd.read_file(str(gadm_path))
    gadm_column = "GID_{}".format(gadm_depth)
    gadm = gadm[[gadm_column, 'geometry']]

    intersects_with_aoi = gadm.intersects(aoi_geom)
    intersected_gadms = gadm[intersects_with_aoi][gadm_column]
    return list(intersected_gadms)

def AoI_intersects_with_blocks(region, aoi_geom, country_code, gadm):
    '''
    Another helper function in generating summary stats for an Area of Interest,
    this will return the list of blocks, within the given gadm, that intersect
    with the Area of Interest

    Inputs:
        - region (str) region consistent with the general data format
        - aoi_geom (Polygon) shapely polygon defining Area of Interest
        - country_code (str) 3-letter country code 
        - gadm (str) gadm containing the blocks we check for intersection
    Outputs:
        - intersected_complexity_pop (GeoDataFrame) complexity-population
                                                    intersecting with AoI
        - intersected_blocks (List[str]) list of gadm's that intersect with AoI
    '''

    # The Landscan processed files contain the blocks so save a step here
    landscan_path = DATA / 'LandScan_Global_2018' / region / country_code
    complexity_pop_path = landscan_path / "complexity_pop_{}.csv".format(gadm)

    if not complexity_pop_path.is_file():
        print("\n\n--Adding the pop data to complexity file for: {}".format(gadm))
        comp_pop_sucess_bool = process_gadm_landscan(region, country_code, gadm)
    else:
        comp_pop_sucess_bool = True

    # If the comp_pop was a success then load it
    if comp_pop_sucess_bool:
        # Load the complexity-population file for that gadm
        complexity_pop = load_complexity_pop(region, country_code, gadm)

        # Get the intersecting blocks
        intersects_with_aoi = complexity_pop.intersects(aoi_geom)
        intersected_complexity_pop = complexity_pop[intersects_with_aoi]
        intersected_blocks = list(intersected_complexity_pop['block_id'])

        return intersected_complexity_pop, intersected_blocks
    # But if not, return None so we can then skip the bad gadm
    else:
        return None, None 

def process_AoI(region, country_code, aoi_geom, aoi_name=""):
    '''
    Given some area of interest, we will find the gadm's that intersect
    the aoi, then the blocks within those gadm's that intersect. We'll
    then return the corresponding block-level complexity w/ Landscan population 
    as well as a list of the intersecting blocks. It also updates the 
    csv which contains a master list of AoI's and the corresponding intersecting
    blocks to expedite later analyses.

    Inputs:
        - region (str) region consistent with the general data format
        - country_code (str) 3-letter country code 
        - aoi_geom (Polygon) shapely polygon defining Area of Interest
        - aoi_name [optional] (str) when saving out the intersecting list of
                         block_ids it may be useful to have an alias for the
                         aoi (i.e. city name)
    '''

    # Get intersecting GADM's
    intersected_gadms = AoI_intersects_with_gadms(aoi_geom, country_code)

    if len(intersected_gadms) == 0:
        print("WARNING -- check AoI {}, it intersects with no GADMS".format(aoi_name))
        return None, None, 

    total_failures = 0
    total_success = 0
    # Loop over each gadm and get the intersecting blocks within that gadm
    for i, gadm in tqdm.tqdm(enumerate(intersected_gadms), total=len(intersected_gadms)):
        intersected_complexity_pop, intersected_blocks = AoI_intersects_with_blocks(region, aoi_geom, country_code, gadm)
        
        # If both intersected_complexity_pop, intersected_blocks are None then we continue
        if intersected_complexity_pop is None and intersected_blocks is None:
            total_failures += 1 
            continue
        else:
            total_success += 1

        if total_success == 1:
            all_intersected_complexity_pop = intersected_complexity_pop
            all_intersected_blocks = intersected_blocks
        else:
            all_intersected_complexity_pop = pd.concat([all_intersected_complexity_pop, intersected_complexity_pop])
            all_intersected_blocks = all_intersected_blocks + intersected_blocks

    # Now update our AoI tracker
    if not AOI_TRACKER.is_file():
        print("\nCreating AoI tracker at: {}".format(AOI_TRACKER))
        aoi_dict = {'aoi_name':[aoi_name], 'aoi_geom':[aoi_geom.wkt], 'gadm_list': [intersected_gadms], 'block_list': [all_intersected_blocks]}
        aoi_tracker = pd.DataFrame.from_dict(aoi_dict)
    else:
        print("\nUpdating AoI tracker...")
        aoi_tracker = pd.read_csv(AOI_TRACKER)
        aoi_record = {'aoi_name':aoi_name, 'aoi_geom':aoi_geom.wkt, 'gadm_list': intersected_gadms, 'block_list': all_intersected_blocks}
        aoi_tracker = aoi_tracker.append(aoi_record, ignore_index=True)
    aoi_tracker.to_csv(AOI_TRACKER, index=False)

    #return all_intersected_complexity_pop, all_intersected_blocks
    return intersected_gadms, all_intersected_blocks

def load_geojson_from_wkt_url(url):

    reply = requests.get(url)
    content = reply.content
    encoding = reply.encoding
    str_content = content.decode(encoding)
    wkt_str = str_content.split(";")[-1].strip()

    return loads(wkt_str)

    # return str_content
    # parsed = json.loads(content.decode(encoding))

    # geoms = parse['geometries']
    # assert len(geoms) == 1, "Check, there's more than 1 geometry in the parsed data"
    # geom_dict = geoms[0]
    # geom_coords = geom_dict['']

def fetch_all_wkt_url(url_df):
    '''
    url_df is a dataframe with columns: aoi_name, wkt_url, wkt_geometry
    This function checks whether any entries have wkt_url but no
    wkt_geometry, indicating it needs to be gathered
    '''

    no_geom = url_df['wkt_geometry'].isna()
    to_download = url_df[no_geom]['wkt_url']
    wkt_geoms = [load_geojson_from_wkt_url(url).wkt for url in to_download]
    
    new_geoms_dict = {'aoi_name':url_df[no_geom]['aoi_name'], 'wkt_geometry':wkt_geoms}
    new_geoms_df = pd.DataFrame(new_geoms_dict)
    url_df.update(new_geoms_df)

    return url_df

def get_aoi_dataset_path(aoi_name):
    p = DATA / 'LandScan_Global_2018' / 'aoi_datasets'
    pt = p / "analysis_{}.csv".format(aoi_name)
    return pt 

def create_aoi_dataset(aoi_name, gadm_list, block_list, region):

    complexity_pop = assemble_complexity_pop(region, gadm_list, block_list)
    complexity_pop['geometry'] = complexity_pop['geometry'].apply(lambda x: x.wkt)
    
    return complexity_pop
    #complexity_pop.to_csv(str(p / "analysis_{}.csv".format(aoi_name)), index=False)


def process_aoi_dataframe(aoi_df):
    aoi_df = aoi_df.loc[aoi_df['wkt_url'] != "not_available"]
    if "wkt_geometry" not in aoi_df.columns:
        aoi_df['wkt_geometry'] = np.nan 
    new_df = fetch_all_wkt_url(aoi_df)

    for i, obs in new_df.iterrows():
        region = obs['region']
        aoi_name = obs['aoi_name']
        country_code = obs['country_code']
        aoi_geom = loads(obs['wkt_geometry'])

        # Has this AoI already been processed into dataset?
        aoi_path = get_aoi_dataset_path(aoi_name)
        if aoi_path.is_file():
            continue
        else:
            print("PROCESSING: {}-{}".format(country_code, aoi_name))
            gadm_list, block_list = process_AoI(region, country_code, aoi_geom, aoi_name)
            if gadm_list is None and block_list is None:
                continue 
            aoi_dataset = create_aoi_dataset(aoi_name, gadm_list, block_list, region)
            aoi_dataset.to_csv(str(aoi_path), index=False)

# Update the aoi tracker to include the geom and intersected blocks for each AoI
p = "../data/city_boundaries/mnp_map_cities.csv"
df = pd.read_csv(p)




#def process_entire_aoi_file(csv_path, )

# if __name__ == "__main__":

#     parser = argparse.ArgumentParser(description='utilities to process LandScan data')
#     subparsers = parser.add_subparsers()

#     # Args for when you just want a single GADM
#     sub_parser_single = subparsers.add_parser('single')
#     sub_parser_single.add_argument('region', type=str, help='Geographic region')
#     sub_parser_single.add_argument('country_code', type=str, help='3-letter country code')
#     sub_parser_single.add_argument('gadm', type=str, help='gadm code')
#     sub_parser_single.set_defaults(func=process_gadm_landscan)
    
#     # Args for doing a directory
#     sub_parser_path = subparsers.add_parser('path')
#     sub_parser_path.add_argument('path_to_complexity_files', type=str, help='path to a complexity folder of which to process')
#     sub_parser_path.set_defaults(func=process_path_landscan)
    
#     args = parser.parse_args()
#     d_args = copy.copy(vars(args))
#     del d_args['func']
#     args.func(**d_args)