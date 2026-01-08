#!/bin/bash

# From user-defined parameter file, find the number jobs to run and submit a job array
# Define the absolute path to the CSV directory
CSV_DIR="/home/j.min/TPC_evolution_SLiM/scripts/01_prepare_input_parameters"
CSV_FILE="${CSV_DIR}/$1"

# Calculate number of jobs (total lines - 1 for header)
NUM_JOBS=$(($(wc -l < "$CSV_FILE") - 1))

echo "Submitting array job with ${NUM_JOBS} tasks for file: ${CSV_FILE}"

# Submit the job with the calculated array size and pass the full path
sbatch --array=1-${NUM_JOBS} run_simulation.sh "$CSV_FILE"