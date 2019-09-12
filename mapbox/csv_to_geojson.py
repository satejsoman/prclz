import getopt, sys
import pandas as pd
import shapely
import fiona
import geopandas as gpd

continent_name = sys.argv[1]

exec(open("/project2/bettencourt/mnp/prclz/prclz/topology.py").read(), globals())

def read_file(path, **kwargs):
    """ ensures geometry set correctly when reading from csv
    otherwise, pd.BlockManager malformed when using gpd.read_file(*) """
    if not path.endswith(".csv"):
        return gpd.read_file(path)
    raw = pd.read_csv(path, **kwargs)
    raw["geometry"] = raw["geometry"].apply(shapely.wkt.loads)
    return gpd.GeoDataFrame(raw, geometry="geometry")

df_csv = read_file("/project2/bettencourt/mnp/prclz/data/tilesets/'{}'.csv").format(continent_name)
df_tile = df_csv[['block_id', 'geometry', 'complexity']]
df_tile.to_file("/project2/bettencourt/mnp/prclz/data/tilesets/'{}'.geojson", driver='GeoJSON').format(continent_name)
