

1. Login to Midway: `ssh <CNETID>@midway2.rcc.uchicago.edu` 

2. Set current directory: `cd /project2/bettencourt/mnp/prclz`

2. Update repo: `git pull`

3. Run script: `bash prclz/parcelization/midway_parcelization.sh`

4. Check jobs: `squeue --user=<CNETID>` 
   And kill jobs: `scancel --user=<CNETID>`
   Run `sinfo -p broadwl` to see a list of allocated/idle nodes
