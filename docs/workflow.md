# Simulation Pipeline

Broadly, each workflow goes through 3 steps before it's ready for plotting in `notebooks/`:

01. Prepare input parameters for SLiM
02. Run SLiM simulations in parallel on cluster
03. Process the output files from SLiM simulations

There are three workflows in current repository. However, one can add a new analysis to the existing pipeline thanks to its modular design. 

## 01. Preparing parameters
Run `01_prepare_input_parameters.py` with following options, depending on what workflow you want to run. 

Todo - describe each option, and how to run it, and what the output is

You can add a new function to scan a different variable.

## 02. Run SLiM
Todo - note that slurm specifics should be modified based on the user's computing resources

## 03. Process outputs
Todo - describe what's being done here


