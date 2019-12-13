import numpy as np 
import rasterio 
from pathlib import Path 
import geopandas as gpd 
from shapely.geometry import MultiPolygon, Polygon, MultiLineString

root = Path('../')
data = root / 'data'


landscan_path = data / 'LandScan_Global_2018' / 'ls_2018.tif'

dataset = rasterio.open(landscan_path)
bounds = dataset.bounds 
resolution = 30 / 3600 # resolution of dataset in degrees

top = bounds.top 
bottom = bounds.bottom 
left = bounds.left 
right = bounds.right 

mat = dataset.read(1)
df_dict = {}
for i, row in enumerate(mat):
    for j, val in enumerate(row):
        cur_top = top + delta * i 
        cur_left = left + delta * j
        cur_bottom = top + delta * (i+1)
        cur_right = left + delta * (j+1)

        # Make the polygon based on the top, left, bottom, right
        poly = Polygon([(cur_top, cur_left), (cur_top, cur_right),
                        (cur_bottom, cur_right), (cur_bottom, cur_left)])
        # Make the observation in the df_dict
        df_dict['geometry'].append(poly)
        df_dict['population'].append(val)

        if (i,j) == (0,0):
            print("Begin at {}, {}".format(cur_top, cur_left))
print("End at {}, {}".format(cur_bottom, cur_right))

# Now make the geopandas object
df = pd.DataFrame.from_dict(df_dict)

# Save 
df.to_csv(data / "worldpop.csv")







