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
conda activate tpc_evo_slim

# Path to csv parameter file - edit based on user name
CSV_FILE="/home/j.min/TPC_evolution_SLiM/\
scripts/01_prepare_input_parameters/\
gaussian_params_unique.csv"

# skip header
LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
PARAMS=$(sed -n "${LINE_NUM}p" "$CSV_FILE")

# Parse CSV - add more variables as needed
IFS=',' read -r RUNTIME BURNIN LOGINTERVAL N_POP\
 RECOVERY GEN_LEN_DEPENDS_ON_TEMP FIXED_GEN_LEN \
 USE_EXTERNAL_TEMP_DATA TEMPDATA_PATH MEAN_TEMP \
 STDEV_TEMP NUM_REP_TEMP_DATA B_default \
 CTmin_default B_critical DeltaB \
 CTmin_critical DeltaCTmin CTmax_critical \
 DeltaCTmax OUTDIR OUTNAME  <<< "$PARAMS"

# The analytical model cannot account for changing generation length
# Thus, define the average generation length here (default is 10)
AVG_GEN_LEN=10

OUTDIR="/projects/lotterhos/TPC_sim_results/data"
echo "Running job ${SLURM_ARRAY_TASK_ID} with \
N_POP=${N_POP}
RECOVERY=${RECOVERY}, \
AVG_GEN_LEN=${AVG_GEN_LEN}, \
MEAN_TEMP=${MEAN_TEMP}, \
STDEV_TEMP=${STDEV_TEMP}, \
B_default=${B_default}, \
CTmin_default=${CTmin_default}, \
B_critical=${B_critical}, \
DeltaB=${DeltaB}, \
CTmin_critical=${CTmin_critical}, \
DeltaCTmin=${DeltaCTmin}, \
CTmax_critical=${CTmax_critical}, \
DeltaCTmax=${DeltaCTmax}, \
OUTDIR=${OUTDIR},\
OUTNAME=${OUTNAME}"

# Run python script for analytical predictions
python -u prediction.py ${RECOVERY} \
${AVG_GEN_LEN} ${MEAN_TEMP} ${STDEV_TEMP} \
${B_default} ${CTmin_default} ${B_critical} \
${DeltaB} ${CTmin_critical} ${DeltaCTmin} \
${CTmax_critical} ${DeltaCTmax} ${OUTDIR }${OUTNAME}

echo "Analytical prediction job finished for output name = ${OUTNAME}"
