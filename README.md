<h1 align="center">p&nbsp;&nbsp;r&nbsp;&nbsp;c&nbsp;&nbsp;l&nbsp;&nbsp;z</h1>
<h6 align="center"> "<i>parcelize</i>" </h6>

### overview/
`prclz` is a library for:
- generating vectors for street blocks in a neighborhood using street network information from [OpenStreetMap](https://www.openstreetmap.org/)
- creating parcels/cadastral maps for building footprints and other land use features within each block 
- calculating structural and areal features (_k_-complexity of access graph, percentage of land used by buildings, etc) at the block and neighborhood level

### development setup/
1. Set up a virtual environment, and activate it.
```
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
```
2. Install the requirements.
```
pip3 install -r requirements.txt
```
3. From the top-level directory, install `prclz` in editable mode.
```
pip3 install -e .
```
4. Deactivate your virtual environment once you're done
```
deactivate
```
----
