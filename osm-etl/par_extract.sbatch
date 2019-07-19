#!/bin/bash
#SBATCH --job-name=MNP
#SBATCH --partition=broadwl
#SBATCH --nodes=1
#SBATCH --ntasks=3
#SBATCH --output=model.out
#SBATCH --error=model.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cnederhood@uchicago.edu
#SBATCH --time=00:30:00
#SBATCH --account=pi-bettencourt

module load Anaconda3/2018.12
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
#
$parallel "$srun ./toy.sh {1}" ::: ../data/input/Africa/* 


 
