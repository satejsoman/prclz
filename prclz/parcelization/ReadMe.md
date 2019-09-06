# Parcelization Job #

## How to run the job ##

1. Login to Midway: `ssh <CNETID>@midway2.rcc.uchicago.edu` 

2. Set current directory: `cd /project2/bettencourt/mnp/prclz`

2. Update repo: `git pull`

3. Run this script to submit jobs: `bash prclz/parcelization/midway_parcelization_residual.sh`

## Midway Help Guide ##

* Check jobs: `squeue --user=<CNETID>` 
    * Kill jobs: `scancel --user=<CNETID>`
    * View allocated/idle nodes `sinfo -p broadwl`
    * Check account balance `rcchelp balance`

* Check error logs: `cd /project2/bettencourt/mnp/prclz/logs`
    * Using a terminal pager to view logs:
      * `less <JOB-NAME>.err`
      * `q` quit
    * Using VIM text editor to view logs:
      * `vim <JOB-NAME>.err`
      * `shift+g` autoscroll to bottom
      * `:q` quit
      * `:wq` save and quit
      * `:q!` quit and don't save
      * `i` insert mode
      * `esc` leave inserty mode and leave command line mode
      
* Setting up Git on Midway:
    * Set current directory to home with `cd` 
    * Run `ssh-keygen` and hit enter at every prompt i.e., leave the following blank `Enter file in which to save the key (/home/nmarchio/.ssh/id_rsa):`, `Enter passphrase (empty for no passphrase):`, `Enter same passphrase again:`
    * Set `cd ~/.ssh` and copy SSH key (view SSH key with `less id_rsa.pub` and hit `q` to exit)
    * Go to github.com, click 'Settings' > 'SSH and GPG keys' > 'New SSH key' and paste in contents of `~/.ssh/id_rsa.pub` and save.
    * To clone the repo `git clone git@github.com:mansueto-institute/prclz.git`
    * To update the local Midway version from the lastest master run `cd /project2/bettencourt/mnp/prclz` then `git pull` 


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
    * Warning `bigmem2` is extremely expensive to use and only use sparingly.
      ```
      module load python/3.7.0
      export MEM_CHECK_INTERVAL=0.01
      python3 monitor_memory.py <insert .R or .py script>
      ```


