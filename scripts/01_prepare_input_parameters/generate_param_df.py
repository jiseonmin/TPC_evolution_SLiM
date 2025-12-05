import argparse
import csv
import itertools
import pandas as pd
# For each workflow, generate two dataframe with parameters (params, params_unique)
# params list all parameter combinations used for SLiM simulation
# params_unique iterate through all but random seeds. This is used for analytical step and to average across replicate simulations. 


# Each parameters have default values as in the master SLiM script. 
params_default = {"seed": 13579,
                  "RUNTIME": 200,
                  "BURNIN": 50,
                  "LOGINTERVAL": 1,
                  "N_POP": 5000,
                  "RECOVERY": 'F',
                  "GEN_LEN_DEPENDS_ON_TEMP": 'T',
                  "FIXED_GEN_LEN": 10,
                  "USE_EXTERNAL_TEMP_DATA": 'T',
                  "TEMPDATA_PATH": "./VT_weather.txt",
                  "MEAN_TEMP": 5,
                  "STDEV_TEMP": 0,
                  "NUM_REP_TEMP_DATA": 20,
                  "B_default": 30,
                  "CTmin_default": 0,
                  "B_critical": 40,
                  "DeltaB": 2,
                  "CTmin_critical": 0,
                  "DeltaCTmin": 2,
                  "CTmax_critical": 40,
                  "DeltaCTmax": 0.2,
                  "OUTDIR": "./data",
                  "OUTNAME": "out"
                  }

# We will use the same order of parameters when saving the dataframes
column_order = ['seed', 'RUNTIME', 'BURNIN', 'LOGINTERVAL', 'N_POP', 'RECOVERY',
        'GEN_LEN_DEPENDS_ON_TEMP', 'FIXED_GEN_LEN', 'USE_EXTERNAL_TEMP_DATA', 
        'TEMPDATA_PATH', 'MEAN_TEMP', 'STDEV_TEMP', 'NUM_REP_TEMP_DATA', 'B_default', 
        'CTmin_default', 'B_critical', 'DeltaB', 'CTmin_critical', 'DeltaCTmin', 
        'CTmax_critical', 'DeltaCTmax', 'OUTDIR', 'OUTNAME']


def gaussian():
    '''
    Assume temperature is Gaussian-distributed.
    Use 3 different mean temperatures, 3 different standard deviations, and repeat for 30 different random seeds.
    Simulation data from this pipeline were used to examine generalist-specialist tradeoff in Min et al. manuscript.
    '''
    param_filename = 'gaussian_params.csv'
    param_unique_filename = 'gaussian_params_unique.csv'

    # List of params to scan
    MEAN_TEMP_list = [5, 20, 35]
    STDEV_TEMP_list = [1, 3, 10]
    seed_list = range(30)
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    RUNTIME = 20_000 # except runtime is edited for one of the mean & stdev combination (see if statement later)
    BURNIN = 5000
    B_default = 31
    CTmin_default = 5
    GEN_LEN_DEPENDS_ON_TEMP = 'F'
    USE_EXTERNAL_TEMP_DATA = 'F'
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    
    # Loop through all combinations of parameters to scan (in this case, MEAN_TEMP, STDEV_TEMP, seed)
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (mean_temp, stdev_temp, seed) in enumerate(itertools.product(MEAN_TEMP_list, STDEV_TEMP_list, seed_list)):
        if (mean_temp == 35) & (stdev_temp == 3):
            # needs extra runtime to equilibrate
            runtime = 40_000
        else:
            runtime = RUNTIME

        new_row = {
                'seed': seed,
                'RUNTIME': runtime,
                'BURNIN': BURNIN,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'USE_EXTERNAL_TEMP_DATA': USE_EXTERNAL_TEMP_DATA,
                'MEAN_TEMP': mean_temp,
                'STDEV_TEMP': stdev_temp,
                'B_default': B_default,
                'CTmin_default': CTmin_default,
                'OUTDIR': OUTDIR,
                'OUTNAME': f"gaussian_MEAN_TEMP_{mean_temp}_STDEV_TEMP_{stdev_temp}_seed_{seed}"
                }
        for key in params_default.keys():
            if key not in new_row.keys():
                new_row[key] = params_default[key]
        params_list.append(new_row)

    # Save the parameter list
    params = pd.DataFrame(params_list)
    # Re-order columns (matches the order in slurm script in next step)
    params = params[column_order]
    # Save as csv file
    params.to_csv(param_filename, index=False)

    # Drop seed and outname columns
    params_unique = params.drop(columns=['seed', 'OUTNAME']).drop_duplicates().reset_index(drop=True)
    # Add OUTNAME again without seed
    params_unique['OUTNAME'] = "gaussian_MEAN_TEMP_" + params_unique['MEAN_TEMP'].astype(str) + "_STDEV_TEMP_" + params_unique['STDEV_TEMP'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)
    

def sine():
    '''
    Assume mean temperature fluctuates sinusoidally between 0 and 35.
    Additionally individuals experience random fluctuation with stdev = 1
    Generate 4 rows choosing whether generation is temperature dependent or not,
    and whether to use recovery or no-recovery model
    '''
    param_filename = 'sine_params.csv'
    param_unique_filename = 'sine_params_unique.csv'

    # List of params to scan
    RECOVERY_list = ['T', 'F']
    GEN_LEN_DEPENDS_ON_TEMP_list = ['T', 'F']
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    RUNTIME = 20_000 
    BURNIN = 5000
    B_default = 31
    CTmin_default = 5
    N_POP = 50_000 # using bigger population to see tracking more clearly
    TEMPDATA_PATH = "./sine.csv"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (recovery, gen_len_depends_on_temp) in enumerate(itertools.product(RECOVERY_list, GEN_LEN_DEPENDS_ON_TEMP_list)):
        new_row = {
                'RUNTIME': RUNTIME,
                'BURNIN': BURNIN,
                'B_default': B_default,
                'CTmin_default': CTmin_default,
                'N_POP': N_POP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'RECOVERY': recovery,
                'GEN_LEN_DEPENDS_ON_TEMP': gen_len_depends_on_temp,
                'OUTNAME': f"sine_RECOVERY_{recovery}_GEN_LEN_DEPENDS_ON_TEMP_{gen_len_depends_on_temp}"
                }
        for key in params_default.keys():
            if key not in new_row.keys():
                new_row[key] = params_default[key]
        params_list.append(new_row)

    # Save the parameter list
    params = pd.DataFrame(params_list)
    # Re-order columns (matches the order in slurm script in next step)
    params = params[column_order]
    # Save as csv file
    params.to_csv(param_filename, index=False)

    # Drop seed and outname columns
    params_unique = params.drop(columns=['seed', 'OUTNAME']).drop_duplicates().reset_index(drop=True)
    # Add OUTNAME again without seed
    params_unique['OUTNAME'] = "sine_RECOVERY_" + \
        params_unique['RECOVERY'].astype(str) + \
            "_GEN_LEN_DEPENDS_ON_TEMP_" + \
                params_unique['GEN_LEN_DEPENDS_ON_TEMP'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare simulation parameters')
    parser.add_argument('--task', type=str, required=True,
                       choices=['gaussian', 'sine'],
                       help='Type of simulation task')
    
    args = parser.parse_args()
    if args.task == 'gaussian':
        print("making parameter files for gaussian task.")
        gaussian()
    elif args.task == 'sine':
        print("making parameter files for sine task.")
        sine()
