

1. Login to Midway: `ssh <CNETID>@midway2.rcc.uchicago.edu` 

2. Set current directory: `cd /project2/bettencourt/mnp/prclz`

2. Update repo: `git pull`

3. Run script: `bash prclz/parcelization/midway_parcelization.sh`

4. Check jobs: `squeue --user=<CNETID>` 
   <p>`And kill jobs: `scancel --user=<CNETID>`
   <p>`Run `sinfo -p broadwl` to see a list of allocated/idle nodes

5. Checking error logs:
   `cd /project2/bettencourt/mnp/prclz/logs`

   Using VIM:
      <p>`vim parcels_SSD.err`</p>
      <p>`:q` quit</p>
      <p>`:wq` save and quit</p>
      <p>`:q!` quit and don't save</p>
      <p>`i` insert mode</p>
      <p>`esc` leave inserty mode and leave command line mode</p>


