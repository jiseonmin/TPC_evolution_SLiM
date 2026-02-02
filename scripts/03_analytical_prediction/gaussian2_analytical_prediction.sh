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
gaussian2_params_unique.csv"

# skip header
LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
PARAMS=$(sed -n "${LINE_NUM}p" "$CSV_FILE")

# Parse CSV - add more variables as needed
IFS=',' read -r RUNTIME_IF_NO_EXTERNAL_TEMP_DATA BURNIN\
 LOGINTERVAL N_POP RECOVERY GEN_LEN_DEPENDS_ON_TEMP\
 FIXED_GEN_LEN USE_EXTERNAL_TEMP_DATA TEMPDATA_PATH\
  MEAN_TEMP STDEV_TEMP NUM_DAYS_TO_REPEAT NUM_REP_TEMP_DATA B_default\
   CTmin_default B_critical DeltaB CTmin_critical\
    DeltaCTmin CTmax_critical DeltaCTmax\
     OUTDIR OUTNAME  <<< "$PARAMS"


# Move to analytical folder and run python script for analytical predictions
ANALYTICS_PATH="/home/j.min/TPC_evolution_SLiM/scripts/03_analytical_prediction"
cd "$ANALYTICS_PATH"

# The analytical model cannot account for changing generation length
# Thus, we will find average generation length from one of the log files
# and use it for analytical prediction
echo "Find a log file from ${OUTDIR} with ${OUTNAME} in its name, calculate average generation length."
AVG_GEN_LEN=$(python find_avg_gen_len.py ${OUTDIR} ${OUTNAME})

echo "USE_EXTERNAL_TEMP_DATA=${USE_EXTERNAL_TEMP_DATA}"
if [[ ${USE_EXTERNAL_TEMP_DATA} == 'T' ]]; then
    echo "Find mean and std of temperature from ${TEMPDATA_PATH}"
    read -r MEAN_TEMP STDEV_TEMP <<< "$(python calculate_mean_std_temp.py ${TEMPDATA_PATH})"
    echo "mean = ${MEAN_TEMP}, stdev = ${STDEV_TEMP}"
fi

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
python -u predict.py ${RECOVERY} \
${AVG_GEN_LEN} ${MEAN_TEMP} ${STDEV_TEMP} \
${B_default} ${CTmin_default} ${B_critical} \
${DeltaB} ${CTmin_critical} ${DeltaCTmin} \
${CTmax_critical} ${DeltaCTmax} ${OUTDIR} ${OUTNAME}

echo "Analytical prediction job finished for output name = ${OUTNAME}"
