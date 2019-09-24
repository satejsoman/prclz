# set up 

- grab midway conda env 
  ```bash
  conda activate mnp 
  conda env export > environment.yml
  ```

- copy the environment to skyway 
  ```bash
  scp environment.yml skyway.rcc.uchicago.edu:
  ```
  
- log in to skyway
  ```bash
  ssh skyway.rcc.uchicago.edu
  ```

- load modules
  ```bash
  module load parallel
  module load anaconda3
  ```

- pull `prclz` repo to cloud home folder 

- 

# resources
- https://github.com/rcc-uchicago/skyway/wiki
- https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
