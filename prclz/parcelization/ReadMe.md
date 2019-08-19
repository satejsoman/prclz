

1. Login to Midway: `ssh <CNETID>@midway2.rcc.uchicago.edu` 

2. Set current directory: `cd /project2/bettencourt/mnp/prclz`

2. Copy repo: `git clone git@github.com:mansueto-institute/prclz.git`

3. Load modules:
```
module load R/3.6.1
module load udunits/2.2
module load gdal/2.4.1 
```
4. Run script: `bash midway_parcelization.sh`
