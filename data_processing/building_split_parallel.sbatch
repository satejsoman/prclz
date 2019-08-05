#!/bin/bash
#SBATCH --job-name=split_buildings_parallel
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --output=model.out
#SBATCH --error=model.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cnederhood@uchicago.edu
#SBATCH --time=06:00:00
#SBATCH --account=pi-bettencourt
#SBATCH --mem=32G

module load parallel

# May be necessary to increase the user process limit
#ulimit -u 10000


# This specifies the options used to run srun. The "-N1 -n1" options are
# used to allocates a single core to each task.
srun="srun --exclusive -N1 -n1"

# This specifies the options used to run GNU parallel:
#
#   --delay of 0.2 prevents overloading the controlling node.
#
#   -j is the number of tasks run simultaneously.
#
#   The combination of --joblog and --resume create a task log that
#   can be used to monitor progress.
#
parallel="parallel --delay 0.2 -j $SLURM_NTASKS --joblog runtask.log --resume"

echo $SLURM_NTASKS

# Run a script, runtask.sh, using GNU parallel and srun. Parallel
# will run the runtask script for the numbers 1 through 128. To
# illustrate, the first job will run like this:
#
#   srun --exclusive -N1 -n1 ./runtask.sh arg1:1 > runtask.1
#

# Call the setup script first
#bash prep_args.sh ../data/geojson/Africa $SLURM_NTASKS
#mkdir output
#mkdir output/tmp

$parallel "$srun python3 ./split_building_files.py {1}" ::: ../data/geojson/Africa/*buildings.geojson
#$parallel "$srun python3 ./split_building_files.py {1} > ./output/{1}.txt" ::: ../data/geojson/Africa/*buildings.geojson 


 
