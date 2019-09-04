import sys
import logging
from logging import info, warning
from pathlib import Path

import geopandas as gpd

from prclz.utils import get_gadm_level_column

filename = sys.argv[1]
output_dir = Path(sys.argv[2])

logging.basicConfig(level=logging.INFO)

gdf = gpd.read_file(filename)
gid_column, level = get_gadm_level_column(gdf)
n = len(gdf)
for i in range(n):
    gid = gdf.iloc[i][gid_column]
    info("%s (%s/%s)", gid, i, n)
    target_path = (output_dir/(gid + ".csv"))
    if not target_path.exists():
        with target_path.open('w') as target:
            gdf.iloc[i:i+1].to_csv(target)
