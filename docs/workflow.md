# Simulation Pipeline

Broadly, each workflow goes through at least 2 steps before it's ready for plotting in `notebooks/`:

1. Prepare input parameters for SLiM
2. Run SLiM simulations in parallel on cluster

In some cases, we go through additional steps. This is mainly for the simplified cases where temperature distirbution is Gaussian and doesn't change across generations.

3. Average evolutionary trajectories across replicate simulations
4. Find expected fitness landscape and expected evolutionary trajectories

There are three workflows in current repository. However, one can add a new analysis to the existing pipeline thanks to its modular design. 

## 01. Preparing parameters
Make a table of parameters used in master SLiM script, formatted like `01_prepare_input_parameters/gaussian_params.csv`, which was created running `generate_param_df.py` with in the same folder (using `--task=gaussian`). 
You can create a similar table however you want, using R, Excel, Google sheets, etc. 
** Important - make sure your file has the same header as the example. **
Read `slim/README.md` for further information of each parameter.

## 02. Run SLiM

### Job array example

`02_run_simulations/example_job_array.sh` is used to submit jobs defined in `01_prepare_input_parameters/gaussian_params.csv` as job array on Northeastern Explorer cluster. It launch 270 jobs, each running one SLiM simulation.

```bash
  sbatch 02_run_simulations/example_job_array.sh
```
You will have to modify the bash script based on your user name, partition you want to use and have access to, etc. See how to modify lines starting with `#SBATCH` from [NURC's documentation](https://rc-docs.northeastern.edu/en/latest/runningjobs/slurmarray.html) or other similar websites from your institution. In addition, change
```
CSV_FILE="/home/j.min/TPC_evolution_SLiM/scripts/01_prepare_input_parameters/gaussian_params.csv"
```
using the path to parameter file you will use. It will be like
```
CSV_FILE="/home/(your-user-name)/TPC_evolution_SLiM/scripts/01_prepare_input_parameters/(your-csv-file).csv"
```
Also change `/home/j.min/TPC_evolution_SLiM/slim/master_WF.slim` from the end of the second to last line with the correct path to the master SLiM script. It's probably going to be `/home/(your-user-name)/TPC_evolution_SLiM/slim/master_WF.slim`

### Single job example
Todo - add an example where only one job is submitted and multiple SLiM simulations run on the same node at the same time. This works well when there are small number of simulations to run (< 10).

## 3. Average trajectories (optional)

Run 03_average_gaussian_log_files.py, which will be generalized to take param files from step 1 and use argparse to select appropriate param files (same choices as 01_prepare_input_parameters.py)

## 4. Expected fitness landscape and expected TPC trajectory (optional)
Run 04_analytical_prediction/gaussian_temp_analytical_prediction.sh for gaussian option. 
Add other similar bash files for different tasks.


