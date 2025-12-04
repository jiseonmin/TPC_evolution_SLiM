# About the master SLiM script for TPC evolution
`master_WF.slim` can be run in SLiMgui or on terminal, overwriting parameters without editing the SLiM script directly.
We recommend using SLiMgui to gain intuition of what's happening in the simulation using their excellent built-in visualization features, 
but move running the script from terminal with a parameter data for serious analyses. 

## Running master SLiM script on SLiMgui
If you don't have SLiMgui 5, install it following Chapter 2 of SLiM manual: [link to SLiM website](https://messerlab.org/slim/)

Open SLiMgui and open `master_WF.slim`. Note that working directory of SLiMgui won't necessarily be where the script is. So click on the folder button to navigate to `TPC_evolution_SLiM/slim`.

Now hit the play button! You will run the simulation with default setting, which we will explain in depth in a later section.

You will see QTNs for B on the chromosome in red and QTNs for CTmin in blue. 

(Put screenshot here)

The script will generate `data` folder in the working directory and start recording custom data every generation in `out.txt`. 
At the end of the simulation, a tree-sequence `out.trees` will be saved also in `data`. 

## Running master SLiM script in command line
If you want to use default parameters as in the SLiM script, run:
```bash
  slim master_WF.slim
```

If you want to use different parameter values, you can do something like:
```bash
  slim -d B_default=20 -d OUTNAME=\'output\' master_WF.slim
```

Here we are editing two parameters, B_default and OUTNAME, to be 20 and 'output'. 
You can easily see why this would be convenient to run many simulations in parallel on a cluster.
We do that using a parameter table saved as .csv file and a slurm script in `scripts`. 
You can read further on the workflow in `scripts/workflow.md` and how to create a new simulation task.
If you want to read more about how to launch SLiM in command line and run jobs in array, check out [slim-sublaunching](https://github.com/slim-community/slim-sublaunching).

## Detailed explantion on SLiM script
`master_WT.slim` simulates TPC evolution in a fixed thermal environment or using an external daily temperature data.
It is a Wright-Fisher simulation (i.e. non-overlapping generation, population is replaced every generation via binomial sampling weighted by fitness) where two key parameters of thermal performance curve (TPC), B and CTmin, are polygenic traits. Fitness is determined by the individual's TPC and a list of daily temperatures experienced by the individual during current generation.

In `Initialize()` block, we set up each chromosome of 100 kbp length to have two neutral regions (each 20kbp long) flanking a QTN region (60kbp long). There are two types of mutations, each for B and CTmin (labeled 'm2', m3'). Neutral mutations (conventionally labeled 'm1') are not simulated in SLiM because we are using tree-sequence recording, and they can be added post-SLiM using `pyslim`. Each mutation arising in QTN region is either QTN for B or CTmin by 50-50 chance, and its effect size is sampled from a Gaussian distribution with zero mean and variance of 0.05. QTN mutation arises with rate of 1e-7. The QTN region is divided into 12 linkage groups, and outside the borders between the linkage groups, recombination happens with uniform rate of 1e-8. 

(Add figure)

Parameters that can be changed in command line are all set up in `Initialize()` block. They include:

- seed (integer): random seed used in SLiM. 
- RUNTIME (integer): total number of generations that simulation runs for. 
- BURNIN (integer): number of generations at the beginning during which QTN mutations accumulates without selection. 
- LOGINTERVAL (integer): information gets logged every LOGINTERVAL generation in a txt file. (integer)
- N_POP (integer): population size (integer)
- RECOVERY (T or F): determines how thermal performance in previous days affect the performance in later days of same generation (boolean)
- GEN_LEN_DEPENDS_ON_TEMP (T or F)
- FIXED_GEN_LEN (integer): number of days in each generation. It is effective only when generation length doesn't depend on temperature.
- USE_EXTERNAL_TEMP_DATA (T or F)
- TEMPDATA_PATH (string): only effective if USE_EXTERNAL_TEMP_DATA is T.
- MEAN_TEMP (integer or float): daily temperature at population level. Only used if USE_EXTERNAL_TEMP_DATA is F.
- STDEV_TEMP (integer or float): controls the temperature variation between individuals in the same population the same day. It is used with or without external temperature data.
- NUM_REP_TEMP_DATA (integer): External temperature data is looped this number of times to run simulation for longer.
- B_default (integer or float): Default breadth of TPC
- CTmin_default (integer or float): Default critical thermal minimum of TPC
- B_critical (integer or float) & DeltaB (integer or float): parameters for fitness component $w_B$, a logistic function penalizing extreme thermal generalist.
- CTmin_critical (integer or float) & DeltaCTmin (integer or float) : parameters for fitness component $w_CTmin$, a logistic function penalizing extreme cold adaptation.
- CTmax_critical (integer or float) & DeltaCTmax (integer or float) : parameters for fitness component $w_CTmax$, a logistic function penalizing extreme heat adaptation.
- OUTDIR (string) : path where output files will be saved. If directory doesn't exist, SLiM will create one.
- OUTNAME (string) : name of the output files, used for both tree-sequence and log file.

All parameters except for OUTDIR and OUTNAME are saved as metadata in tree-sequence output at the end of simulation.

At BURNIN generation, log file is generated with these columns:
- cycle
- day
- Temp
- B_mean
- B_sd
- CTmin_mean
- CTmin_sd
- CTmax_mean
- CTmax_sd
- Topt_mean
- Topt_sd
- fitness_mean
- fitness_sd

Note that cycle is same as generation, since this is a Wright-Fisher simulation. 'day' is the first day of the generation; 0 corresponds to the first temperature in the external temperature data. Temp is the daily temperature on 'day' at population level (i.e. doesn't consider individual variation). Mean and standard deviation of various parameters are calculated among the individuals alived at each generation. 

Todo
- How to format external daily temperature data - requires a temperature column to be under 'T2M'.
