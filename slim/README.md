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

## Running master SLiM script on terminal
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

## Detailed explantion on SLiM script
`master_WF.slim` has several editable parameters. 
However, as described earlier, none of the parameter needs to be defined outside the script.

The parameters are
(list the parameters)

(Talk about what happens in the simulation)



