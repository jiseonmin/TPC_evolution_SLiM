#!/bin/bash
#SBATCH --job-name=TPC_evol_sim
#SBATCH --output=/scratch/j.min/slurm_out/job_%A_%a.out
#SBATCH --error=/scratch/j.min/slurm_err/job_%A_%a.err
#SBATCH --array=1-270
#SBATCH --time=0-12:00:00
#SBATCH --mem=4G
#SBATCH --partition=lotterhos
#SBATCH --cpus-per-task=1

module load anaconda3
eval "$(conda shell.bash hook)"
conda activate tpc_evo_slim

# Path to csv parameter file - edit based on user name
CSV_FILE="/home/j.min/TPC_evolution_SLiM/scripts/01_prepare_input_parameters/gaussian_params.csv"

# skip header
LINE_NUM=$((SLURM_ARRAY_TASK_ID + 1))
PARAMS=$(sed -n "${LINE_NUM}p" "$CSV_FILE")

# Parse CSV - add more variables as needed
IFS=',' read -r seed RUNTIME BURNIN\
 LOGINTERVAL N_POP RECOVERY GEN_LEN_DEPENDS_ON_TEMP\
 FIXED_GEN_LEN USE_EXTERNAL_TEMP_DATA TEMPDATA_PATH\
  MEAN_TEMP STDEV_TEMP NUM_REP_TEMP_DATA B_default\
   CTmin_default B_critical DeltaB CTmin_critical\
    DeltaCTmin CTmax_critical DeltaCTmax\
     OUTDIR OUTNAME  <<< "$PARAMS"

echo "Running job ${SLURM_ARRAY_TASK_ID} \
with seed=${seed} RUNTIME=${RUNTIME} BURNIN=${BURNIN} \
LOGINTERVAL=${LOGINTERVAL} N_POP=${N_POP} RECOVERY=${RECOVERY}\
 GEN_LEN_DEPENDS_ON_TEMP=${GEN_LEN_DEPENDS_ON_TEMP} \
 FIXED_GEN_LEN=${FIXED_GEN_LEN} USE_EXTERNAL_TEMP_DATA=${USE_EXTERNAL_TEMP_DATA}\
  TEMPDATA_PATH=${TEMPDATA_PATH} MEAN_TEMP=${MEAN_TEMP}\
   STDEV_TEMP=${STDEV_TEMP} NUM_REP_TEMP_DATA=${NUM_REP_TEMP_DATA}\
    B_default=${B_default} CTmin_default=${CTmin_default}\
     B_critical=${B_critical} DeltaB=${DeltaB} \
     CTmin_critical=${CTmin_critical} DeltaCTmin=${DeltaCTmin} CTmax_critical=${CTmax_critical} \
     DeltaCTmax=${DeltaCTmax} OUTDIR=${OUTDIR} OUTNAME=${OUTNAME}"

# Move to slim path
SLIM_PATH="/home/j.min/TPC_evolution_SLiM/slim"
cd "$SLIM_PATH"

# Run slim script (check the absolute path of the slim script)
slim -d seed=${seed} -d RUNTIME=${RUNTIME} -d BURNIN=${BURNIN} \
-d LOGINTERVAL=${LOGINTERVAL} -d N_POP=${N_POP} -d RECOVERY=${RECOVERY} \
-d GEN_LEN_DEPENDS_ON_TEMP=${GEN_LEN_DEPENDS_ON_TEMP} \
-d FIXED_GEN_LEN=${FIXED_GEN_LEN} \
-d USE_EXTERNAL_TEMP_DATA=${USE_EXTERNAL_TEMP_DATA}\
 -d TEMPDATA_PATH=\'${TEMPDATA_PATH}\' \
 -d MEAN_TEMP=${MEAN_TEMP} -d STDEV_TEMP=${STDEV_TEMP} \
 -d NUM_REP_TEMP_DATA=${NUM_REP_TEMP_DATA} \
 -d B_default=${B_default} -d CTmin_default=${CTmin_default} \
 -d B_critical=${B_critical} -d DeltaB=${DeltaB} \
 -d CTmin_critical=${CTmin_critical} -d DeltaCTmin=${DeltaCTmin}\
  -d CTmax_critical=${CTmax_critical} -d DeltaCTmax=${DeltaCTmax}\
   -d OUTDIR=\'${OUTDIR}\' -d OUTNAME=\'${OUTNAME}\' \
   master_WF.slim

echo "slim simulation finished. output name = ${OUTNAME}"
