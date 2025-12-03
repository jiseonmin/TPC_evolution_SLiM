# A general model for evolution of thermal performance curves (TPC)

We provide a master SLiM script for simulating TPC evolution where TPC parameters are assumed as polygenic traits. This is a repository is complementary to a manuscript in prepartion, but can be adapted for various user-defined temperature data.

## Citation

If you use this code, please cite our paper (will be edited when paper is preprinted):

Min J, Chapman Z, ..., & Lotterhos KE. A general model for the evolution of thermal performance curves with application to real time-series data

## Quick Start

1. Clone the repository
```bash
   git clone https://github.com/jiseonmin/TPC_evolution_SLiM.git
   cd TPC_evolution_SLiM
```

2. Set up the conda environment
```bash
   conda env create -f environment.yml
   conda activate tpc_evo_slim
```

Now you are ready to run simulations!

## Running simulations

See `docs/workflow.md` for detailed instructions. 

## Repository Structure
- `slim/` - Master SLiM script and documentation
- `scripts/` - Parameter preparation, execution, and analysis scripts
- `data/` - Input data (tracking only small input data)
- `results/` - Output figures and tables
- `docs/` - Detailed documentation
- `notebooks/` - Notebooks for generating manuscript figures and interactive notebooks
