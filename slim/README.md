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

The script will generate `data` folder outside `slim` and start recording custom data every generation in `out.txt`. 
At the end of the simulation, a tree-sequence `out.trees` will be saved also in `data`. 
In addition, `out.csv` contains list of B and CTmin of 100 randomly sampled individuals in the last 100 generations of the simulation.

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

## Detailed explantion on SLiM script (work in progress)
`master_WT.slim` simulates TPC evolution in a fixed thermal environment or using an external daily temperature data.
It is a Wright-Fisher simulation (i.e. non-overlapping generation, population is replaced every generation via binomial sampling weighted by fitness) where two key parameters of thermal performance curve (TPC), B and CTmin, are quantitative traits. Fitness is determined by the individual's TPC, a list of daily temperatures in population level (`DAILY_TEMPS_AT_CURRENT_GEN`, see lines 194 to 202), how much individual temperature deviates from the population mean, and environmental noise (`epsilon` in line 217).

In `Initialize()` block, we set up each chromosome of 100 kbp length to have two neutral regions (each 20kbp long) flanking a QTN region (60kbp long). There are two types of mutations, each for B and CTmin (labeled 'm2', m3'). Neutral mutations (conventionally labeled 'm1') are not simulated in SLiM because we are using tree-sequence recording, and they can be added post-SLiM using `pyslim`. Each mutation arising in QTN region is either QTN for B or CTmin by 50-50 chance, and its effect size is sampled from a Gaussian distribution with zero mean and variance of 0.05. QTN mutation arises with rate of 1e-7. The QTN region is divided into 12 linkage groups, and outside the borders between the linkage groups, recombination happens with uniform rate of 1e-8. 

(Add figure)

Parameters that can be changed in command line are all set up in `Initialize()` block. They include:

- seed (integer): random seed used in SLiM. 
- RUNTIME_IF_NO_EXTERNAL_TEMP_DATA (integer): total number of generations that simulation runs for if no external temperature data is used. If external temperature data is being used, this variable isn't used: instead, runtime is calculated based on the number of times first few days of data is repeated and whether number of days per generation depends on temperature--see lines 123 to 139 and a custom function `true_runtime` defined in line 322 to 229.
- BURNIN (integer): number of generations at the beginning during which QTN mutations accumulates neutrally--see `fitnessEffect()` block (lines 215 to 240) where fitness is 1 for all individuals while `sim.cycle <= BURNIN`.
- LOGINTERVAL (integer): information gets logged every LOGINTERVAL generation in a txt file.
- N_POP (integer): population size in the Wright-Fisher simulation (i.e. not necessarily equal to census population size). In our current simulation, the population stays constant.
- RECOVERY (T or F): determines how thermal performance in previous days affect the performance in later days of same generation--see line 285 to 300 in `fitness_function()`. 
- GEN_LEN_DEPENDS_ON_TEMP (T or F): If true, length of each generation is determined by the temperature on the first day of a given generation--see a custom function `gen_len()` in lines 307 to 320 to see how temperature on the first day of a generation maps to the length of generation. If false, generation length is equal to FIXED_GEN_GEN for the entirety of the simulation.
- FIXED_GEN_LEN (integer): number of days in each generation. It is effective only when generation length doesn't depend on temperature.
- USE_EXTERNAL_TEMP_DATA (T or F) : If true, a daily temperature data is imported from TEMPDATA_PATH. As in two example input files, `sine.csv` and `VT_weather.txt`, daily temperature is recorded in a column with header "T2M"--see line 125.
- TEMPDATA_PATH (string): only effective if USE_EXTERNAL_TEMP_DATA is T.
- MEAN_TEMP (integer or float): daily temperature at population level. Only used if USE_EXTERNAL_TEMP_DATA is F.
- STDEV_TEMP (integer or float): controls the temperature variation between individuals in the same population the same day. 
- NUM_DAYS_TO_REPEAT (integer): First NUM_DAYS_TO_REPEAT of the external temperature data is repeated to run simulation longer if temperature data is limited--see lines 126 to 135.
- NUM_REP_TEMP_DATA (integer): After this number of cycling through the first few days, the remaining temperature data is used just once till the end of simulation--see lines 126 to 135.
- B_default (integer or float): Default breadth of TPC
- CTmin_default (integer or float): Default critical thermal minimum of TPC
- B_critical (integer or float) & DeltaB (integer or float): parameters for fitness component $w_B$, a logistic function penalizing extreme thermal generalist.
- CTmin_critical (integer or float) & DeltaCTmin (integer or float) : parameters for fitness component $w_{CTmin}$, a logistic function penalizing extreme cold adaptation.
- CTmax_critical (integer or float) & DeltaCTmax (integer or float) : parameters for fitness component $w_{CTmax}$, a logistic function penalizing extreme heat adaptation.
- OUTDIR (string) : path where output files will be saved. If directory doesn't exist, SLiM will create one.
- OUTNAME (string) : name of the output files, including a tree-sequence (`[OUTNAME].trees`), log file (`[OUTNAME].txt`), and a csv file containing sample $B$ and $CTmin$ (`[OUTNAME].csv`).

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

Note that 'cycle' means generation for Wright-Fisher simulations in SLiM. 'day' is the first day of the generation; 0 corresponds to the first temperature in the external temperature data. Temp is the daily temperature on 'day' at population level (i.e. doesn't consider individual variation). Mean and standard deviation of various parameters are calculated among all individuals present in 'cycle' generation. 

Lastly, in the last 100 generations of simulation, 100 individuals are randomly drawn from the population, and their $B$ and $CTmin$ are appended to a vector named `LINES`, which is saved as a csv file at the end of the simulation.

# Other slim scripts in this folder
There are some variation of `master_WF.slim` that were used in the paper.

- `scramble_temp_data.slim`: samples daily temperature from timeseries data with uniform weights. Used for Figure S15 non-autocorrelated VT curve.

- `two_normal.slim`: Sample temperature from a mixture of two normal distributions, instead of a single Gaussian distribution. Used for Figure S5.

- `variable_N.slim`: a WF simulation where population size at each generation is determined by the body temperature on the first day of that generation. Not used in the manuscript.

- `master_WF_include_sd_pop.slim`: Compared to the constant environment simulations where mean body temperature is constant and individual adds noise independently, this script lets you add noise to the mean temperature itself. Not used in the manuscript.