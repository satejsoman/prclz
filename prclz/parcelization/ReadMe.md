# Parcelization Job #

## How to run the job ##

1. Login to Midway: `ssh <CNETID>@midway2.rcc.uchicago.edu` 

2. Set current directory: `cd /project2/bettencourt/mnp/prclz`

2. Update repo: `git pull`

3. Run script: `bash prclz/parcelization/midway_parcelization.sh`

## Midway Help Guide ##

* Check jobs: `squeue --user=<CNETID>` 
    * Kill jobs: `scancel --user=<CNETID>`
    * View allocated/idle nodes `sinfo -p broadwl`

* Check error logs: `cd /project2/bettencourt/mnp/prclz/logs`
    * Using VIM which functions as a text editor to view logs:
      * `vim <JOB-NAME>.err`
      * `:q` quit
      * `:wq` save and quit
      * `:q!` quit and don't save
      * `shift+g` autoscroll to bottom
      * `i` insert mode
      * `esc` leave inserty mode and leave command line mode

* Sort by file size in directory:
    * `cd /project2/bettencourt/mnp/prclz/data/geojson_gadm/Africa/SLE`
    * `ls -l | sort -k 5nr`

* SLURM source docs: https://slurm.schedmd.com/sbatch.html 


