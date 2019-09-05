# Parcelization Job #

## How to run the job ##

1. Login to Midway: `ssh <CNETID>@midway2.rcc.uchicago.edu` 

2. Set current directory: `cd /project2/bettencourt/mnp/prclz`

2. Update repo: `git pull`

3. Run this first script: `bash prclz/parcelization/midway_parcelization.sh`

4. Run this script second to catch failures: `bash prclz/parcelization/midway_parcelization_residual.sh`

## Midway Help Guide ##

* Check jobs: `squeue --user=<CNETID>` 
    * Kill jobs: `scancel --user=<CNETID>`
    * View allocated/idle nodes `sinfo -p broadwl`

* Check error logs: `cd /project2/bettencourt/mnp/prclz/logs`
    * Using less terminal pager to view logs:
      * `less <JOB-NAME>.err`
      * `q` quit
    * Using VIM which functions as a text editor to view logs:
      * `vim <JOB-NAME>.err`
      * `shift+g` autoscroll to bottom
      * `:q` quit
      * `:wq` save and quit
      * `:q!` quit and don't save
      * `i` insert mode
      * `esc` leave inserty mode and leave command line mode

* Sort by file size in directory:
    * `cd /project2/bettencourt/mnp/prclz/data/buildings/Africa/SLE`
    * `ls -l | sort -k 5nr`

* Transfer files: 
    * Transfer Midway file to local directory `scp nmarchio@midway.rcc.uchicago.edu:/project2/bettencourt/mnp/prclz/data/buildings/Africa/SLE/buildings_SLE.4.2.1_1.geojson /Users/nmarchio/Desktop`
    * Transfer Midway folder to local directory `scp -r nmarchio@midway.rcc.uchicago.edu:/project2/bettencourt/mnp/prclz/data/complexity/Africa/SLE /Users/nmarchio/Desktop`
    * Transfer local folder to Midway directory `scp -r /Users/nmarchio/Desktop/SLE_CSV nmarchio@midway.rcc.uchicago.edu:/project2/bettencourt/mnp/prclz/data/mapbox_test`

* SLURM source docs: https://slurm.schedmd.com/sbatch.html 
    * Generally `--mem = 58000` is upper limit allowed on `broadwl` and this represents the memory allocated to the node
    * To check memory useage [use this script](https://github.com/rcc-uchicago/R-large-scale/blob/master/monitor_memory.py) and run the following:
      ```
      module load python/3.7.0
      export MEM_CHECK_INTERVAL=0.01
      python3 monitor_memory.py <insert .R or .py script>
      ```


