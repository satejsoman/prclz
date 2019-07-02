# PRCLZ

## 
`prclz` is a library for:
- generating vectors for street blocks in a neighborhood using street network information from (OpenStreetMap)
- creating parcels/cadastral maps for building footprints and other land use features within each block 
- calculating structural and areal features (_k_-complexity of access graph, percentage of land used by buildings, etc) at the block and neighborhood level

## Development Setup
1. Set up a virtual environment, and activate it.
```
pip install virtualenv
virtualenv venv
source venv/bin/activate
```
2. Install the requirements.
```
pip install -r requirements.txt
```
3. From the top-level directory, install `topology` in editable mode.
```
pip install -e .
```
4. Deactivate your virtual environment once you're done
```
deactivate
```
----
