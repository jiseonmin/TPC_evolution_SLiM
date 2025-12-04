# About the master SLiM script for TPC evolution
`master_WF.slim` can be run in SLiMgui or on terminal, overwriting parameters without editing the SLiM script directly.
We recommend using SLiMgui to gain intuition of what's happening in the simulation using their excellent built-in visualization features, 
but move running the script from terminal with a parameter data for serious analyses. 

## Running master SLiM script on SLiMgui
Note on working directory

Note on what's visible (QTNs for B and CTmin)

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

## Detailed explantion on SLiM script
Explain parameters and what happens in each generation, what's in the output files.
