#!/bin/bash
#SBATCH --job-name=A1_sims
#SBATCH --output=/scratch/j.min/slurm_out/job_%A_%a.out
#SBATCH --error=/scratch/j.min/slurm_err/job_%A_%a.err
#SBATCH --array=1-270
#SBATCH --time=0-12:00:00
#SBATCH --mem=4G
#SBATCH --partition=lotterhos
#SBATCH --cpus-per-task=1

module load anaconda3
eval "$(conda shell.bash hook)"
conda activate dsuzukii_env

# Path to csv parameter file
CSV_FILE="A1_nr_params.csv"

# skip header
LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
PARAMS=$(sed -n "${LINE_NUM}p" "$CSV_FILE")

# Parse CSV - add more variables as needed
IFS=',' read -r run_id muT sigmaT seed N RUNTIME B_WT CTmin_WT OUTNAME <<< "$PARAMS"

# set the absolute path of where the output should go to - modify if needed
OUTDIR="/projects/lotterhos/TPC_sim_results/data"
echo "Running job ${SLURM_ARRAY_TASK_ID} with muT=${muT}, sigmaT=${sigmaT}, N=${N}, seed=${seed}, RUNTIME=${RUNTIME}, B_WT=${B_WT}, CTmin_WT=${CTmin_WT}, OUTNAME=${OUTNAME}"

# Run slim script (check the absolute path of the slim script)
slim -d Recovery=F -d T_mean=${muT} -d sigma_T_within_gen=${sigmaT} -d N_POP=${N} -d seed=${seed} -d RUNTIME=${RUNTIME} -d B_WT=${B_WT} -d CTmin_WT=${CTmin_WT} -d OUTNAME=\'${OUTNAME}\' -d OUTDIR=\'${OUTDIR}\' /home/j.min/D.Suzukii_SLiMulation/SLiM_scripts/single_pop_no_acclimation.slim

echo "slim simulation finished. output name = ${OUTNAME}"
