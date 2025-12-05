#!/bin/bash
#SBATCH --job-name=TPC_evol_sim_parallel
#SBATCH --output=/scratch/j.min/slurm_out/job_%j.out
#SBATCH --error=/scratch/j.min/slurm_err/job_%j.err
#SBATCH --time=0-12:00:00
#SBATCH --mem=20G
#SBATCH --partition=lotterhos
#SBATCH --cpus-per-task=5

module load anaconda3
eval "$(conda shell.bash hook)"
conda activate tpc_evo_slim

CSV_FILE="/home/j.min/TPC_evolution_SLiM/scripts/01_prepare_input_parameters/sine_params.csv"

TOTAL_LINES=$(tail -n +2 "$CSV_FILE" | wc -l)
echo "Running $TOTAL_LINES simulations in parallel"

# Move to slim path
SLIM_PATH="/home/j.min/TPC_evolution_SLiM/slim"
cd "$SLIM_PATH"

# Loop through all parameter rows
while IFS=',' read -r seed RUNTIME BURNIN LOGINTERVAL N_POP RECOVERY GEN_LEN_DEPENDS_ON_TEMP FIXED_GEN_LEN USE_EXTERNAL_TEMP_DATA TEMPDATA_PATH MEAN_TEMP STDEV_TEMP NUM_REP_TEMP_DATA B_default CTmin_default B_critical DeltaB CTmin_critical DeltaCTmin CTmax_critical DeltaCTmax OUTDIR OUTNAME; do
    
    echo "Starting simulation: ${OUTNAME}"
    
    # Run slim in background, redirect output to individual log files
    (
        slim -d seed=${seed} \
             -d RUNTIME=${RUNTIME} \
             -d BURNIN=${BURNIN} \
             -d LOGINTERVAL=${LOGINTERVAL} \
             -d N_POP=${N_POP} \
             -d RECOVERY=${RECOVERY} \
             -d GEN_LEN_DEPENDS_ON_TEMP=${GEN_LEN_DEPENDS_ON_TEMP} \
             -d FIXED_GEN_LEN=${FIXED_GEN_LEN} \
             -d USE_EXTERNAL_TEMP_DATA=${USE_EXTERNAL_TEMP_DATA} \
             -d TEMPDATA_PATH=\'${TEMPDATA_PATH}\' \
             -d MEAN_TEMP=${MEAN_TEMP} \
             -d STDEV_TEMP=${STDEV_TEMP} \
             -d NUM_REP_TEMP_DATA=${NUM_REP_TEMP_DATA} \
             -d B_default=${B_default} \
             -d CTmin_default=${CTmin_default} \
             -d B_critical=${B_critical} \
             -d DeltaB=${DeltaB} \
             -d CTmin_critical=${CTmin_critical} \
             -d DeltaCTmin=${DeltaCTmin} \
             -d CTmax_critical=${CTmax_critical} \
             -d DeltaCTmax=${DeltaCTmax} \
             -d OUTDIR=\'${OUTDIR}\' \
             -d OUTNAME=\'${OUTNAME}\' \
             master_WF.slim
        
        echo "$(date): Finished ${OUTNAME}"
    ) &
    
done < <(tail -n +2 "$CSV_FILE")

# Wait for all background jobs to complete
echo "Waiting for all simulations to complete..."
wait

echo "All simulations finished at $(date)!"