import argparse
import csv
import itertools
import pandas as pd
# For each workflow, generate two dataframe with parameters (params, params_unique)
# params list all parameter combinations used for SLiM simulation
# params_unique iterate through all but random seeds. This is used for analytical step and to average across replicate simulations. 


# Each parameters have default values as in the master SLiM script. 
params_default = {"seed": 13579,
                  "RUNTIME_IF_NO_EXTERNAL_TEMP_DATA": 200,
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
                  "NUM_DAYS_TO_REPEAT": 365,
                  "NUM_REP_TEMP_DATA": 2,
                  "B_default": 31,
                  "CTmin_default": 5,
                  "B_critical": 40,
                  "DeltaB": 2,
                  "CTmin_critical": 0,
                  "DeltaCTmin": 2,
                  "CTmax_critical": 40,
                  "DeltaCTmax": 0.2,
                  "OUTDIR": "../data",
                  "OUTNAME": "out"
                  }

# We will use the same order of parameters when saving the dataframes
column_order = ['seed', 'RUNTIME_IF_NO_EXTERNAL_TEMP_DATA', 'BURNIN', 'LOGINTERVAL', 'N_POP', 'RECOVERY',
        'GEN_LEN_DEPENDS_ON_TEMP', 'FIXED_GEN_LEN', 'USE_EXTERNAL_TEMP_DATA', 
        'TEMPDATA_PATH', 'MEAN_TEMP', 'STDEV_TEMP', 'NUM_DAYS_TO_REPEAT', 'NUM_REP_TEMP_DATA', 'B_default', 
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
    RUNTIME_IF_NO_EXTERNAL_TEMP_DATA = 20_000 # except runtime is edited for one of the mean & stdev combination (see if statement later)
    BURNIN = 5000
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
            runtime_if_no_external_temp_data = 40_000
        else:
            runtime_if_no_external_temp_data = RUNTIME_IF_NO_EXTERNAL_TEMP_DATA

        new_row = {
                'seed': seed,
                'RUNTIME_IF_NO_EXTERNAL_TEMP_DATA': runtime_if_no_external_temp_data,
                'BURNIN': BURNIN,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'USE_EXTERNAL_TEMP_DATA': USE_EXTERNAL_TEMP_DATA,
                'MEAN_TEMP': mean_temp,
                'STDEV_TEMP': stdev_temp,
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

def gaussian2():
    '''
    Same as gaussian except for lower critical B, beyond which w_TPC is lowered significantly due to physiological cost.
    '''
    param_filename = 'gaussian2_params.csv'
    param_unique_filename = 'gaussian2_params_unique.csv'

    # List of params to scan
    MEAN_TEMP_list = [5, 20, 35]
    STDEV_TEMP_list = [1, 3, 10]
    seed_list = range(30)
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    B_critical = 20
    RUNTIME_IF_NO_EXTERNAL_TEMP_DATA = 20_000 # except runtime is edited for one of the mean & stdev combination (see if statement later)
    BURNIN = 5000
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
            runtime_if_no_external_temp_data = 40_000
        else:
            runtime_if_no_external_temp_data = RUNTIME_IF_NO_EXTERNAL_TEMP_DATA

        new_row = {
                'seed': seed,
                'RUNTIME_IF_NO_EXTERNAL_TEMP_DATA': runtime_if_no_external_temp_data,
                'B_critical': B_critical,
                'BURNIN': BURNIN,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'USE_EXTERNAL_TEMP_DATA': USE_EXTERNAL_TEMP_DATA,
                'MEAN_TEMP': mean_temp,
                'STDEV_TEMP': stdev_temp,
                'OUTDIR': OUTDIR,
                'OUTNAME': f"gaussian2_MEAN_TEMP_{mean_temp}_STDEV_TEMP_{stdev_temp}_seed_{seed}"
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
    params_unique['OUTNAME'] = "gaussian2_MEAN_TEMP_" + params_unique['MEAN_TEMP'].astype(str) + "_STDEV_TEMP_" + params_unique['STDEV_TEMP'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)    

def two_normal():
    '''
    Sample temperature from a mixture of two equally weighted normal distribution
    Control the seperation of the mean while keeping the total mean and variance constant
    We can do this by setting mean = MEAN_TEMP + or - SEP_MEAN / 2, 
    variance = STDEV_TEMP^2 - SEP_MEAN ^ 2 / 4 for each normal distribution.

    Todo : make a new .slim that samples individual daily temperature from two normal distributions
    (pick either of them by 50-50 chance and add random variable from only that distribution.)
    '''
    param_filename = 'two_normal_params.csv'
    param_unique_filename = 'two_normal_params_unique.csv'
    # this task needs one extra parameter (SEP_MEAN_TEMP) before STDEV_TEMP
    idx = column_order.index('STDEV_TEMP')
    column_order.insert(idx, 'SEP_MEAN_TEMP')

    # scan separation between peaks (0 to 2 * STDEV_TEMP, which is the maximum separation)
    SEP_MEAN_TEMP_list = [1, 5, 10, 20]
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    RUNTIME_IF_NO_EXTERNAL_TEMP_DATA = 20_000 # except runtime is edited for one of the mean & stdev combination (see if statement later)
    BURNIN = 5000
    GEN_LEN_DEPENDS_ON_TEMP = 'F'
    USE_EXTERNAL_TEMP_DATA = 'F'
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
    MEAN_TEMP = 20
    STDEV_TEMP = 10

    # Other params will use values from params_default

    
    # Loop through all combinations of parameters to scan (in this case, MEAN_TEMP, STDEV_TEMP, seed)
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, SEP_MEAN_TEMP in enumerate(SEP_MEAN_TEMP_list):

        new_row = {
                'RUNTIME_IF_NO_EXTERNAL_TEMP_DATA': RUNTIME_IF_NO_EXTERNAL_TEMP_DATA,
                'BURNIN': BURNIN,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'USE_EXTERNAL_TEMP_DATA': USE_EXTERNAL_TEMP_DATA,
                'MEAN_TEMP': MEAN_TEMP,
                'SEP_MEAN_TEMP': SEP_MEAN_TEMP,
                'STDEV_TEMP': STDEV_TEMP,
                'OUTDIR': OUTDIR,
                'OUTNAME': f"two_normal_SEP_MEAN_TEMP_{SEP_MEAN_TEMP}"
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
    params_unique['OUTNAME'] = "two_normal_SEP_MEAN_TEMP_" + params_unique['SEP_MEAN_TEMP'].astype(str) 
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
    NUM_DAYS_TO_REPEAT = 3600
    NUM_REP_TEMP_DATA = 200
    # number of generation will be around NUM_DAYS_TO_REPEAT * NUM_REP_TEMP_DATA / 30 to / 10
    BURNIN = 5000
    STDEV_TEMP = 1
    TEMPDATA_PATH = "./sine.csv"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (recovery, gen_len_depends_on_temp) in enumerate(itertools.product(RECOVERY_list, GEN_LEN_DEPENDS_ON_TEMP_list)):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
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

def sine2():
    '''
    Repeat the sine example with different population sizes (N=500, 5k, or 50k) and different random seeds
    Testing how N influence adaptive tracking pattern and variability across replicate simulations
    '''
    param_filename = 'sine2_params.csv'
    param_unique_filename = 'sine2_params_unique.csv'

    # List of params to scan
    N_list = [500, 5000, 50_000]
    seed_list = range(30)
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    NUM_DAYS_TO_REPEAT = 3600
    NUM_REP_TEMP_DATA = 100
    GEN_LEN_DEPENDS_ON_TEMP = 'F'

    # number of generation will be NUM_DAYS_TO_REPEAT * NUM_REP_TEMP_DATA / 10
    BURNIN = 5000
    STDEV_TEMP = 1
    TEMPDATA_PATH = "./sine.csv"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (N, seed) in enumerate(itertools.product(N_list, seed_list)):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'N_POP': N,
                'seed': seed,
                'OUTNAME': f"sine2_N_{N}_seed_{seed}"
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
    params_unique['OUTNAME'] = "sine2_N_" + \
        params_unique['N_POP'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)    

def sine_test():
    '''
    Repeat the sine example with different hyperparameters to see if amplitude of CTmin oscillation
    can be increased.
    '''
    param_filename = 'sine_test_params.csv'
    param_unique_filename = 'sine_test_params_unique.csv'
    # First, try default values (same as gaussian example)
    # Change either CTmin_critical or B_critical in each simulation 
    # while keeping the other to its default value.
    # lastly, try modifying both.
    new_params = [(params_default["B_critical"], params_default["CTmin_critical"]), 
                    (20, params_default["CTmin_critical"]), 
                    (params_default["B_critical"], 4), 
                    (20, 4)]
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    NUM_DAYS_TO_REPEAT = 3600
    NUM_REP_TEMP_DATA = 100
    GEN_LEN_DEPENDS_ON_TEMP = 'F'
    # number of generation will be NUM_DAYS_TO_REPEAT * NUM_REP_TEMP_DATA / 10
    BURNIN = 5000
    STDEV_TEMP = 1
    TEMPDATA_PATH = "./sine.csv"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (B_critical, CTmin_critical) in enumerate(new_params):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'CTmin_critical': CTmin_critical,
                'B_critical': B_critical,
                'OUTNAME': f"sine_test_CTmin_critical_{CTmin_critical}_B_critical_{B_critical}"
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
    params_unique['OUTNAME'] = "sine_test_CTmin_critical_" + \
        params_unique['CTmin_critical'].astype(str) + "_B_critical_" + \
        params_unique['B_critical'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)    


def vermont():
    '''
    Use vermont NASA POWER data for mean temperature,
    and add random fluctuation with stdev = 1
    Generate 4 rows choosing whether generation is temperature dependent or not,
    and whether to use recovery or no-recovery model
    '''
    param_filename = 'VT_params.csv'
    param_unique_filename = 'VT_params_unique.csv'

    # List of params to scan
    RECOVERY_list = ['T', 'F']
    GEN_LEN_DEPENDS_ON_TEMP_list = ['T', 'F']
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    # cycle through data from 2015-1-1 to 2020-12-31, 200 times
    NUM_DAYS_TO_REPEAT = 2192
    NUM_REP_TEMP_DATA = 200

    BURNIN = 5000
    STDEV_TEMP = 1
    N_POP = 5000
    TEMPDATA_PATH = "./VT_weather.txt"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (recovery, gen_len_depends_on_temp) in enumerate(itertools.product(RECOVERY_list, GEN_LEN_DEPENDS_ON_TEMP_list)):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
                'N_POP': N_POP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'RECOVERY': recovery,
                'GEN_LEN_DEPENDS_ON_TEMP': gen_len_depends_on_temp,
                'OUTNAME': f"VT_RECOVERY_{recovery}_GEN_LEN_DEPENDS_ON_TEMP_{gen_len_depends_on_temp}"
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
    params_unique['OUTNAME'] = "VT_RECOVERY_" + \
        params_unique['RECOVERY'].astype(str) + \
            "_GEN_LEN_DEPENDS_ON_TEMP_" + \
                params_unique['GEN_LEN_DEPENDS_ON_TEMP'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)

def kentucky():
    '''
    Use KY NASA POWER data for mean temperature,
    and add random fluctuation with stdev = 1
    '''
    param_filename = 'KY_params.csv'
    param_unique_filename = 'KY_params_unique.csv'

    # List of parameters to change from default values, but keep constant across all simulations
    # cycle through data from 1981-1-1 to 1986-12-31, 200 times
    NUM_DAYS_TO_REPEAT = 2191
    NUM_REP_TEMP_DATA = 200

    # List of params to scan
    GEN_LEN_DEPENDS_ON_TEMP_list = ['T', 'F']

    RECOVERY = 'F'
    BURNIN = 5000
    STDEV_TEMP = 1
    N_POP = 5000
    TEMPDATA_PATH = "./KY_timeseries.csv"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, gen_len_depends_on_temp in enumerate(GEN_LEN_DEPENDS_ON_TEMP_list):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
                'N_POP': N_POP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'RECOVERY': RECOVERY,
                'GEN_LEN_DEPENDS_ON_TEMP': gen_len_depends_on_temp,
                'OUTNAME': f"KY_GEN_LEN_DEPENDS_ON_TEMP_{gen_len_depends_on_temp}"
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
    params_unique['OUTNAME'] = "KY_GEN_LEN_DEPENDS_ON_TEMP_" + \
                params_unique['GEN_LEN_DEPENDS_ON_TEMP'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)       
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare simulation parameters')
    parser.add_argument('--task', type=str, required=True,
                       choices=['gaussian', 'gaussian2', 'two_normal', 'sine', 'sine2', 'sine_test', 'vermont', 'kentucky'],
                       help='Type of simulation task')
    
    args = parser.parse_args()
    if args.task == 'gaussian':
        print("making parameter files for gaussian task.")
        gaussian()
    elif args.task == 'gaussian2':
        print("making parameter files for gaussian2 task.")
        gaussian2()
    if args.task == 'two_normal':
        print("making parameter files for two normal distributions task.")
        two_normal()
    elif args.task == 'sine':
        print("making parameter files for sine task.")
        sine()
    elif args.task == 'sine2':
        print("making parameter files for sine2 task.")
        sine2()
    elif args.task == 'sine_test':
        print("making parameter files for sine (test) task.")
        sine_test()
    elif args.task == 'vermont':
        print("making parameter files for vermont task.")
        vermont()
    elif args.task == 'kentucky':
        print("making parameter files for kentucky task.")
        kentucky()
