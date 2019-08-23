

1. Login to Midway: `ssh <CNETID>@midway2.rcc.uchicago.edu` 

2. Set current directory: `cd /project2/bettencourt/mnp/prclz`

2. Update repo: `git pull`

3. Run script: `bash prclz/parcelization/midway_parcelization.sh`

4. Check jobs: `squeue --user=<CNETID>` 
   * And kill jobs: `scancel --user=<CNETID>`
   * Run `sinfo -p broadwl` to see a list of allocated/idle nodes

5. Checking error logs:
   `cd /project2/bettencourt/mnp/prclz/logs`

   Using VIM:
      * `vim <JOB-NAME>.err`
      * `:q` quit
      * `:wq` save and quit
      * `:q!` quit and don't save
      * `shift+g` autoscroll to bottom
      * `i` insert mode
      * `esc` leave inserty mode and leave command line mode

6. Rank order file sizes:
    * `cd /project2/bettencourt/mnp/prclz/data/geojson_gadm/Africa/SLE`
    * `ls -l | sort -k 5nr`

7. SLURM source docs: https://slurm.schedmd.com/sbatch.html 


