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

Here run a bash script with the name of the parameter file you would like to use. For instance, for the sine task, run:
```bash
chmod +x submit_jobs.sh
./submit_jobs.sh sine_params.csv
```
You should see something like:
```
Submitting array job with 4 tasks for file: /home/[username]/TPC_evolution_SLiM/scripts/01_prepare_input_parameters/sine_params.csv
Submitted batch job [job number]
```
Note that You will have to modify the bash script based on your username, partition you want to use and have access to, etc. See how to modify lines starting with `#SBATCH` from [NURC's documentation](https://rc-docs.northeastern.edu/en/latest/runningjobs/slurmarray.html) or a similar website from your institution. In addition, you should modify the path to csv file based on where the project folder is. For example, if you cloned this repository in home directory, you need to use
```bash
CSV_DIR="/home/(your-username)/TPC_evolution_SLiM/scripts/01_prepare_input_parameters"
```
in `submit_job_array.sh`. Similarly, you should also change the path to slim folder
```bash
SLIM_PATH="/home/(your-username)/TPC_evolution_SLiM/slim"
```
Finally, you might want to modify `submit_job_array.sh` to run simulations using only a subset of parameters if the parameter file is too long (e.g. gaussian example has 270 lines). For instance, `sbatch --array=3-10 run_simulation.sh "$CSV_FILE"` to launch 8 jobs, using line 3 to 10 of the csv file.  
***The example parameter files set OUDIR (directory where SLiM outputs are save) to the Lotterhos lab storage space. If you are not on the NU cluster and/or do not have access to `projects/lotterhos`, you need to change OUDIR to something else. The default value (`../data`) should work.***

## 03. Expected fitness landscape and expected TPC trajectory (optional)
Here, we use helper functions from `tpc_functions_oo.py` to calculate expected fitness landscape, optimal B and CTmin that maximizes expected fitness, and path from initial B and CTmin and optimal B and CTmin predicted from solving a differential equation numerically.
The theoretical model assumes temperature to be Gaussian distributed and generation length to be constant.
You can submit a job array to carry out the calculation for each row of parameter files in parallel by running
```bash
sbatch analytical_prediction.sh gaussian_params_unique.csv
```
replacing `gaussian_params_unique.csv` for the appropriate filename.

If the simulations are set to run with fixed generation length, you can launch the jobs without completing step 2, Run SLiM. But if the generation length depends on temperature, log files will be used, running `find_avg_gen_len.py`. 

Adjust lines starting with `#SBATCH` as needed. 


## 04. Average trajectories and visualize (optional)
`04_average_and_visualize_logged_data.py` averages the log files created from 'gaussian' workflow across the replicate simulations. It also generates a diagnostic figure that plots some of the logged parameters against generation time. 
