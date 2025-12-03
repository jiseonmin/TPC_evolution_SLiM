# Simulation Pipeline

Broadly, each workflow goes through at least 2 steps before it's ready for plotting in `notebooks/`:

1. Prepare input parameters for SLiM
2. Run SLiM simulations in parallel on cluster

In some cases, we go through additional steps. This is mainly for the simplified cases where temperature distirbution is Gaussian and doesn't change across generations.

3. Average evolutionary trajectories across replicate simulations
4. Find expected fitness landscape and expected evolutionary trajectories

There are three workflows in current repository. However, one can add a new analysis to the existing pipeline thanks to its modular design. 

## 01. Preparing parameters
Run `01_prepare_input_parameters.py` with following options, depending on what workflow you want to run. 

### Temperature sampled from a fixed normal distribution
Run
```bash
  python 01_prepare_input_parameters.py gaussian
```
It will generate csv file where each row defines input parameters that will be read in by SLiM in the next step. Here, temperature is sampled from a Gaussian distribution each day with mean = 5, 20, or 35 and standard deviation = 1, 3, or 10. Each of 9 simulation is repeated for 30 times with random seed 0 to 29. 

### Other options - todo
By adding a function to `01_prepare_input_parameters.py`, one create a new parameter files for SLiM to use.

## 02. Run SLiM
Todo - note that slurm specifics should be modified based on the user's computing resources
### Temperature sampled from a fixed normal distribution
On a cluster, run
```bash
  sbatch 02_run_simulations/gaussian_temp.sh
```
This will lauch a slurm job-array.

### other options -- todo

One can add a new bash script similarly formatted as the existing bash scripts for a new task.

## 3. Average trajectories (optional)

Run 03_average_gaussian_log_files.py, which will be generalized to take param files from step 1 and use argparse to select appropriate param files (same choices as 01_prepare_input_parameters.py)

## 4. Expected fitness landscape and expected TPC trajectory (optional)
Run 04_analytical_prediction/gaussian_temp_analytical_prediction.sh for gaussian option. 
Add other similar bash files for different tasks.


