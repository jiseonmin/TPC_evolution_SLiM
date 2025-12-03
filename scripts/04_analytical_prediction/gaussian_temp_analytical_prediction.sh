#!/bin/bash
#SBATCH --job-name=analytical
#SBATCH --output=/scratch/j.min/slurm_out/job_%A_%a.out
#SBATCH --error=/scratch/j.min/slurm_err/job_%A_%a.err
#SBATCH --array=1-9
#SBATCH --time=0-05:00:00
#SBATCH --mem=4G
#SBATCH --partition=short
#SBATCH --cpus-per-task=1

module load anaconda3
eval "$(conda shell.bash hook)"
conda activate dsuzukii_env

# Path to csv parameter file
CSV_FILE="A1_nr_params_unique.csv"

# skip header
LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
PARAMS=$(sed -n "${LINE_NUM}p" "$CSV_FILE")

# Parse CSV - add more variables as needed
IFS=',' read -r muT sigmaT N RUNTIME B_WT CTmin_WT OUTNAME <<< "$PARAMS"

OUTDIR="/projects/lotterhos/TPC_sim_results/data"
echo "Running job ${SLURM_ARRAY_TASK_ID} with muT=${muT}, sigmaT=${sigmaT}, N=${N}, RUNTIME=${RUNTIME}, B_WT=${B_WT}, CTmin_WT=${CTmin_WT}, OUTNAME=${OUTNAME}"

# Run python script for analytical predictions
python -u 3_analytical_prediction.py ${muT} ${sigmaT} ${B_WT} ${CTmin_WT} ${OUTNAME}

echo "Analytical prediction job finished for output name = ${OUTNAME}"
