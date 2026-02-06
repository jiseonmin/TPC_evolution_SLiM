#!/bin/bash
#SBATCH --job-name=TPC_evol_singular
#SBATCH --output=/scratch/j.min/slurm_out/job_%A.out
#SBATCH --error=/scratch/j.min/slurm_err/job_%A.err
#SBATCH --time=2-00:00:00
#SBATCH --mem=4G
#SBATCH --partition=lotterhos
#SBATCH --cpus-per-task=1

# submit singular slim simulations using default parameters

module load anaconda3
eval "$(conda shell.bash hook)"
conda activate tpc_evo_slim

# Move to slim path
SLIM_PATH="/home/j.min/TPC_evolution_SLiM/slim"
cd "$SLIM_PATH"
slim scramble_temp_data.slim
echo -e "scrambled VT sim done."