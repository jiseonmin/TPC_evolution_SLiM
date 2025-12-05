# Simulation Pipeline

Broadly, each workflow goes through at least 2 steps before it's ready for analysis (see `notebooks/` for examples):

1. Prepare input parameters for SLiM
2. Run SLiM simulations in parallel on cluster
3. Make analytical prediction

Once the SLiM simulations are finished (step 2), you are ready to analyze the outputs. 
Step 3 is for comparing analytical theory and simulation, which can be optional.

If you repeated same simulations with different random seed, you can 

4. Average evolutionary trajectories across replicate simulations and each trajectory along with the average trajectory

There are two workflows in current repository: 'gaussian' and 'sine'. However, one can add a new analysis to the existing pipeline thanks to its modular design. 

## 01. Preparing parameters
Make a table of parameters used in master SLiM script, formatted like `01_prepare_input_parameters/gaussian_params.csv` or `sine_params.csv`, which were created running `generate_param_df.py` in the same folder (using `--task=gaussian` or `--task=sine`). 
You can create a similar table however you want, using R, Excel, Google sheets, etc. 
***Important - make sure your file has the same header as the examples.***
Read `slim/README.md` for further information of each parameter.
Both example tasks have a similar looking csv file without seed column and OUTNAME without seed (`gaussian_params_unique.csv` and `sine_params_unique.csv`). 
These are used in step 3 and 4 and are not necessary for running SLiM on cluster (step 2).

## 02. Run SLiM

### Job array example

`02_run_simulations/example_job_array.sh` is used to submit jobs defined in `01_prepare_input_parameters/gaussian_params.csv` as job array on Northeastern Explorer cluster. It launch 270 jobs, each running one SLiM simulation.

```bash
  sbatch 02_run_simulations/example_job_array.sh
```
You will have to modify the bash script based on your user name, partition you want to use and have access to, etc. See how to modify lines starting with `#SBATCH` from [NURC's documentation](https://rc-docs.northeastern.edu/en/latest/runningjobs/slurmarray.html) or a similar website from your institution. In addition, change
```
CSV_FILE="/home/j.min/TPC_evolution_SLiM/scripts/01_prepare_input_parameters/gaussian_params.csv"
```
using the path to parameter file you will use. It will be like
```
CSV_FILE="/home/(your-user-name)/TPC_evolution_SLiM/scripts/01_prepare_input_parameters/(your-csv-file).csv"
```
Also change the path to SLiM script:
```
SLIM_PATH="/home/j.min/TPC_evolution_SLiM/slim"
```
to something like `/home/(your-user-name)/TPC_evolution_SLiM/slim`

### Single job example
`02_run_simulations/example_single_job.sh` submit a single job which runs 4 SLiM simulations in parallel. 
This approach is useful if you are running small number of simulations (<10). 
Similar to the job array example, change the first few lines and path to csv and slim files before running the bash script.

## 03. Expected fitness landscape and expected TPC trajectory (optional)
Here, we use helper functions from `tpc_functions_oo.py` to calculate expected fitness landscape, optimal B and CTmin that maximizes expected fitness, and path from initial B and CTmin and optimal B and CTmin predicted from solving a differential equation numerically.
The theoretical model assumes temperature to be Gaussian distributed and generation length to be constant.
Currently, there is one bash script that will generate an .npz file for each line in `gaussian_params_unique.csv`. 
One can use it for a different task by changing `CSV_FILE` and `AVG_GEN_LEN` appropriately along with the first few lines starting with `#SBATCH` appropriately, as described in step 2.

## 04. Average trajectories and visualize (optional)
`04_average_and_visualize_logged_data.py` averages the log files created from 'gaussian' workflow across the replicate simulations. It also generates a diagnostic figure that plots some of the logged parameters against generation time. 
