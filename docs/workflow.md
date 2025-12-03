# Simulation Pipeline

Broadly, each workflow goes through 3 steps before it's ready for plotting in `notebooks/`:

01. Prepare input parameters for SLiM
02. Run SLiM simulations in parallel on cluster
03. Process the output files from SLiM simulations

There are three workflows in current repository. However, one can add a new analysis to the existing pipeline thanks to its modular design. 

## 01. Preparing parameters
Run `01_prepare_input_parameters.py` with following options, depending on what workflow you want to run. 

### Temperature sampled from a fixed normal distribution
Run
```
python 01_prepare_input_parameters.py gaussian
```
It will generate csv file where each row defines input parameters that will be read in by SLiM in the next step. Here, temperature is sampled from a Gaussian distribution each day with mean = 5, 20, or 35 and standard deviation = 1, 3, or 10. Each of 9 simulation is repeated for 30 times with random seed 0 to 29. 

### Other options - todo
By adding a function to `01_prepare_input_parameters.py`, one create a new parameter files for SLiM to use.

## 02. Run SLiM
Todo - note that slurm specifics should be modified based on the user's computing resources
### Temperature sampled from a fixed normal distribution
On a cluster, run
```
sbatch 02_run_simulations/gaussian_temp.sh
```
This will lauch a slurm job-array.

### other options -- todo

One can add a new bash script similarly formatted as the existing bash scripts for a new task.

## 03. Process outputs
Todo - describe what's being done here


