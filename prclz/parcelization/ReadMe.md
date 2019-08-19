

1. Login to Midway. 

2. Copy repo: `git clone git@github.com:mansueto-institute/prclz.git`

3. Install R packages.
`module load R/3.5.1`
```
install.packages(
pkgs=c('sf','tidyr','dplyr','purrr','lwgeom','stringr','parallel','foreach','doParallel'),
repos="http://cran.r-project.org", 
lib="~/local/R_libs/"))
```
