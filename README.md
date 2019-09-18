<h1 align="center">p&nbsp;&nbsp;r&nbsp;&nbsp;c&nbsp;&nbsp;l&nbsp;&nbsp;z</h1>
<h6 align="center"> "<i>parcelize</i>" </h6>

### overview/
`prclz` is a library for:
- generating vectors for street blocks in a neighborhood using street network information from [OpenStreetMap](https://www.openstreetmap.org/)
- creating parcels/cadastral maps for building footprints and other land use features within each block 
- calculating structural and areal features (_k_-complexity of access graph, percentage of land used by buildings, etc) at the block and neighborhood level


### structure/
- [`prclz`](/prclz): main library
    - [`blocks`](/prclz/blocks): extract vector polygons representing street blocks from street network information
    - [`features`](/prclz/features): calculate per-block features
    - [`parcels`](/prclz/parcels): generate cadastral parcels tesselating each block given building/land use footprints
    - [`topology`](/prclz/topology): planar graph implementation, with tools to calculate weak duals. largely taken from [openreblock/topology](https://github.com/open-reblock/topology).

- [`smoketests`](/smoketests): not _quite_ unit tests, but visual tests to make sure things look right

- [`osm-etl`](/osm-etl): scripts to perform ETL on `*.osm.pbf` files and extract relevant features.

- [`midway`](/midway): end-to-end workflow to be run on RCC's [`midway` cluster](https://rcc.uchicago.edu/docs/using-midway/index.html)

- [`requirements`](/requirements): required packages

### development setup/
0. on midway, load the necessary modules
```
module load intel/18.0
module load gdal/2.2
module unload python
module load Anaconda3/5.1.0
module load parallel
```
1. Set up a conda virtual environment, and activate it.
```
. .midway/conda_setup.sh
conda create --name mnp
source activate mnp
```
2. Install the requirements. (Due to version pinning/compatibility, some packages aren't in the standard conda repos, so we install them with `pip`).
```
conda install --name mnp -f -y -q -c anaconda -c conda-forge --file requirements/conda-requirements.txt
pip3 install -r requirements/pip-requirements.txt
```
3. From the top-level directory, install `prclz` in editable mode.
```
pip3 install -e .
```
4. Deactivate your virtual environment once you're done
```
conda deactivate
```
----
