import argparse
import itertools
import pandas as pd
import numpy as np
import sys
sys.path.insert(1, '../03_analytical_prediction')
from tpc_functions_oo import *
# For each workflow, generate two dataframe with parameters (params, params_unique)
# params list all parameter combinations used for SLiM simulation
# params_unique iterate through all but random seeds. This is used for analytical step and to average across replicate simulations. 


# Each parameters have default values as in the master SLiM script. 
params_default = {"seed": 13579,
                  "RUNTIME_IF_NO_EXTERNAL_TEMP_DATA": 200,
                  "BURNIN": 50,
                  "LOGINTERVAL": 1,
                  "N_POP": 5000,
                  "MU": 1e-7,
                  "QTN_var": 0.05,
                  "RECOMBINATION_RATE": 1e-8,
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
column_order = ['seed', 'RUNTIME_IF_NO_EXTERNAL_TEMP_DATA', 'BURNIN', 'LOGINTERVAL', 'N_POP', 
                'MU', 'QTN_var', 'RECOMBINATION_RATE', 'RECOVERY', 'GEN_LEN_DEPENDS_ON_TEMP', 'FIXED_GEN_LEN', 
                'USE_EXTERNAL_TEMP_DATA', 'TEMPDATA_PATH', 'MEAN_TEMP', 'STDEV_TEMP', 
                'NUM_DAYS_TO_REPEAT', 'NUM_REP_TEMP_DATA', 'B_default', 
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

def gaussian_alt_initial():
    '''
    Alternative default values (and initial values) of B and CTmin (B=5, CTmin=33)
    '''
    param_filename = 'gaussian_alt_initial_params.csv'
    param_unique_filename = 'gaussian_alt_initial_params_unique.csv'

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
    B_default=5
    CTmin_default=33
 
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
                'OUTNAME': f"gaussian_alt_initial_MEAN_TEMP_{mean_temp}_STDEV_TEMP_{stdev_temp}_seed_{seed}",
                'B_default': B_default,
                'CTmin_default': CTmin_default
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
    params_unique['OUTNAME'] = "gaussian_alt_initial_MEAN_TEMP_" + params_unique['MEAN_TEMP'].astype(str) + "_STDEV_TEMP_" + params_unique['STDEV_TEMP'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)

def temp_trop():
    '''
    Comparing extreme temperate and tropical populations further.
    Set default B and CTmin to be same distance and fitness away from theoretical optimum in both environments.
    Test for three population sizes (500, 5k, 50k)
    Repeat for 30 random seeds
    '''

    param_filename = 'temp_trop_params.csv'
    param_unique_filename = 'temp_trop_params_unique.csv'

    # List of params to scan
    seed_list = range(30)
    N_list = [500, 5000, 50_000]
    # OUTNAME will reflect the change of these parameters


    # find B_default and CTmin_default that is half-way between tropical and temperate

    tpc_object = tpc_functions()

    MEAN_TEMP_AND_STDEV_TEMP = [(35, 1), (20, 10)]
    # Among the muT and sigmaT's used in A1, select two combinations that represent tropical and temperate environments
    muT_trop = MEAN_TEMP_AND_STDEV_TEMP[0][0]
    sigmaT_trop = MEAN_TEMP_AND_STDEV_TEMP[0][1]
    muT_temp = MEAN_TEMP_AND_STDEV_TEMP[1][0]
    sigmaT_temp = MEAN_TEMP_AND_STDEV_TEMP[1][1]
    # We want to find initial B and CTmin that are equidistant from the theoretical optima from both conditions, and have the same starting fitness
    datadir = "../../data/"

    analytical_info_trop = np.load(f"{datadir}gaussian_MEAN_TEMP_{muT_trop}_STDEV_TEMP_{sigmaT_trop}_analytical_info.npz", allow_pickle=True)
    analytical_info_temp = np.load(f"{datadir}gaussian_MEAN_TEMP_{muT_temp}_STDEV_TEMP_{sigmaT_temp}_analytical_info.npz", allow_pickle=True)
    x1 = analytical_info_trop['B_opt']
    x2 = analytical_info_temp['B_opt']
    y1 = analytical_info_trop['CTmin_opt']
    y2 = analytical_info_temp['CTmin_opt']


    def CTmin_equidistant(B):
        CTmin = (x2**2 - x1**2 + y2**2 - y1**2) / (2 * (y2-y1)) - (x2-x1) / (y2-y1) * B
        return CTmin

    def diff_fitness(B):
        CTmin = CTmin_equidistant(B)
        # Given B, find CTmin that is equidistant from (x1,y1) and (x2,y2)
        fit1 = tpc_object.expected_w_TPC_no_recovery(CTmin=CTmin, 
            B=B, 
            muT=muT_trop,
            sigmaT=sigmaT_trop)
        fit2 = tpc_object.expected_w_TPC_no_recovery(CTmin=CTmin,
            B=B,
            muT=muT_temp,
            sigmaT=sigmaT_temp)
        if fit1 < 1e-3:
            return 10
        else:
            return np.abs(fit1-fit2)
    B_default=0.1
    diff = diff_fitness(B_default)
    while diff > 5e-4:
        B_default += 1e-2
        CTmin_default = CTmin_equidistant(B_default)
        if B_default + CTmin_default > 40:
            print("CTmax too big. No root found")
            break
        else:
            diff = diff_fitness(B_default)

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
    for i, ((mean_temp, stdev_temp), seed, N) in enumerate(itertools.product(MEAN_TEMP_AND_STDEV_TEMP, seed_list, N_list)):
        new_row = {
                'seed': seed,
                'RUNTIME_IF_NO_EXTERNAL_TEMP_DATA': RUNTIME_IF_NO_EXTERNAL_TEMP_DATA,
                'BURNIN': BURNIN,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'USE_EXTERNAL_TEMP_DATA': USE_EXTERNAL_TEMP_DATA,
                'MEAN_TEMP': mean_temp,
                'STDEV_TEMP': stdev_temp,
                'OUTDIR': OUTDIR,
                'OUTNAME': f"MEAN_TEMP_{mean_temp}_STDEV_TEMP_{stdev_temp}_N_{N}_seed_{seed}",
                'B_default': B_default,
                'CTmin_default': CTmin_default,
                'N_POP':N
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
    params_unique['OUTNAME'] = "MEAN_TEMP_" + params_unique['MEAN_TEMP'].astype(str) \
        + "_STDEV_TEMP_" + params_unique['STDEV_TEMP'].astype(str)\
            + "_N_" + params_unique['N_POP'].astype(str)
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
    SEP_MEAN_TEMP_list = [14, 17, 19, 19.9]
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    RUNTIME_IF_NO_EXTERNAL_TEMP_DATA = 20_000 # except runtime is edited for one of the mean & stdev combination (see if statement later)
    BURNIN = 5000
    GEN_LEN_DEPENDS_ON_TEMP = 'F'
    USE_EXTERNAL_TEMP_DATA = 'F'
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
    MEAN_TEMP = 5
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

def include_sd_pop():
    '''
    Adding shared thermal noise for all individuals in current population
    (i.e. thermal noise is sum of individual and population noise)
    This uses a different slim script, and there is an additional column (like two-normal case)
    Don't make params_unique because analytical prediction doesn't distinguish sd_individual or sd_pop
    '''
    param_filename = 'include_sd_pop_params.csv'
    param_unique_filename = 'include_sd_pop_params_unique.csv'
    # this task needs extra parameterS (STDEV_TEMP_POP) and (STDEV_TEMP_INDIVIDUAL) and no STDEV_TEMP
    idx = column_order.index('STDEV_TEMP')
    column_order.insert(idx, 'STDEV_TEMP_INDIVIDUAL')
    column_order.insert(idx, 'STDEV_TEMP_POP')
    column_order.pop(idx+2)
    print(column_order)

    # Creating list of parameters
    # Keep total variance (stdev) constant, change the proportion from 0 to 1
    STDEV_TEMP = 10

    prop_pop_var_list = np.linspace(0, 1, 11)
    seed_list = range(30)

    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    RUNTIME_IF_NO_EXTERNAL_TEMP_DATA = 20_000 # except runtime is edited for one of the mean & stdev combination (see if statement later)
    BURNIN = 5000
    GEN_LEN_DEPENDS_ON_TEMP = 'F'
    USE_EXTERNAL_TEMP_DATA = 'F'
    OUTDIR = "/scratch/j.min/TPC_evol_SLiM"
    MEAN_TEMP = 35

    # Other params will use values from params_default

    
    # Loop through all combinations of parameters to scan (in this case, seed, proportion of var_ind)
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (seed, prop_pop_var) in enumerate(itertools.product(seed_list, prop_pop_var_list)):
        stdev_temp_pop = STDEV_TEMP * np.sqrt(prop_pop_var)
        stdev_temp_individual = np.sqrt(STDEV_TEMP ** 2 - stdev_temp_pop ** 2)
        new_row = {
                'RUNTIME_IF_NO_EXTERNAL_TEMP_DATA': RUNTIME_IF_NO_EXTERNAL_TEMP_DATA,
                'BURNIN': BURNIN,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'USE_EXTERNAL_TEMP_DATA': USE_EXTERNAL_TEMP_DATA,
                'MEAN_TEMP': MEAN_TEMP,
                'STDEV_TEMP_INDIVIDUAL': stdev_temp_individual,
                'STDEV_TEMP_POP': stdev_temp_pop,
                'seed': seed,
                'OUTDIR': OUTDIR,
                'OUTNAME': f"include_STDEV_POP_prop_{prop_pop_var:.1f}_seed_{seed}"
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


def sine_test():
    '''
    Assume mean temperature fluctuates sinusoidally between 0 and 35 using sine.csv.
    Additionally individuals experience random fluctuation with stdev = 1
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

def sine2():
    '''
    Repeat the sine example with different population sizes (N=500, 5k, or 50k) and different random seeds
    Testing how N influence adaptive tracking pattern and variability across replicate simulations
    Based on sine_test, use B_critical = 20 to make adaptive tracking more visible
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
    B_critical = 20
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
                'B_critical': B_critical,
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


def sine3():
    '''
    Repeat the sine example with fixed generation length or variable generation length and different random seeds
    When gen length is fixed, it is set to 22, so that the average length is roughly the same between the two cases.
    Based on sine_test, use B_critical = 20 to make adaptive tracking more visible
    '''
    param_filename = 'sine3_params.csv'
    param_unique_filename = 'sine3_params_unique.csv'

    # List of params to scan
    GEN_LEN_DEPENDS_ON_TEMP_list = ['T', 'F']
    seed_list = range(30)
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    NUM_DAYS_TO_REPEAT = 3600
    NUM_REP_TEMP_DATA = 100
    FIXED_GEN_LEN = 22
    B_critical = 20
    # number of generation will be NUM_DAYS_TO_REPEAT * NUM_REP_TEMP_DATA / 10
    BURNIN = 5000
    STDEV_TEMP = 1
    TEMPDATA_PATH = "./sine.csv"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (GEN_LEN_DEPENDS_ON_TEMP, seed) in enumerate(itertools.product(GEN_LEN_DEPENDS_ON_TEMP_list, seed_list)):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'FIXED_GEN_LEN': FIXED_GEN_LEN,
                'B_critical': B_critical,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'seed': seed,
                'OUTNAME': f"sine3_GEN_LEN_DEPENDS_ON_TEMP_{GEN_LEN_DEPENDS_ON_TEMP}_seed_{seed}"
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
    params_unique['OUTNAME'] = "sine3_GEN_LEN_DEPENDS_ON_TEMP_" + \
        params_unique['GEN_LEN_DEPENDS_ON_TEMP'].astype(str)
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)    

def sine4():
    '''
    Repeat the sine example with different mutation rate and variance of effect sizes to test how GA affects efficacy of seasonal adaptation.
    Based on sine_test, use B_critical = 20 to make adaptive tracking more visible
    '''
    param_filename = 'sine4_params.csv'
    param_unique_filename = 'sine4_params_unique.csv'

    # List of params to scan
    MU_AND_QTN_VAR = [(1e-7, 0.05), (1e-8, 25), (1e-8, 50), (1e-8, 300), (1e-9, 300), (1e-6, 0.005), (1e-5, 0.0005)]
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    # List of parameters to change from default values, but keep constant across all simulations
    NUM_DAYS_TO_REPEAT = 3600
    NUM_REP_TEMP_DATA = 100
    GEN_LEN_DEPENDS_ON_TEMP = 'F'
    B_critical = 20
    B_default = 20
    CTmin_default = 10
    # number of generation will be NUM_DAYS_TO_REPEAT * NUM_REP_TEMP_DATA / 10
    BURNIN = 5000
    STDEV_TEMP = 1
    TEMPDATA_PATH = "./sine.csv"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, (MU, QTN_var) in enumerate(MU_AND_QTN_VAR):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'B_critical': B_critical,
                'B_default': B_default,
                'CTmin_default': CTmin_default,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'MU': MU,
                'QTN_var': QTN_var,
                'OUTNAME': f"sine4_MU_{MU}_QTN_var_{QTN_var}"
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
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)    

def vermont():
    '''
    Use vermont NASA POWER data for mean temperature, use same hyperparameters as KY example in manuscript
    repeat with 5 different seeds
    '''
    param_filename = 'VT_params.csv'
    param_unique_filename = 'VT_params_unique.csv'

    # List of params to scan
    seed_list = range(5)
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    # cycle through data from 2015-1-1 to 2020-12-31, 200 times
    NUM_DAYS_TO_REPEAT = 2192
    NUM_REP_TEMP_DATA = 20

    MU = 1e-6
    FIXED_GEN_LEN = 21
    GEN_LEN_DEPENDS_ON_TEMP = 'F'
    B_default = 30
    CTmin_default = 0
    B_critical = 30
    CTmin_critical = 1.5
    CTmax_critical = 40

    BURNIN = 5000
    STDEV_TEMP = 0
    N_POP = 5000
    TEMPDATA_PATH = "./VT_weather.txt"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, seed in enumerate(seed_list):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'MU': MU,
                'FIXED_GEN_LEN': FIXED_GEN_LEN,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'B_default': B_default,
                'CTmin_default': CTmin_default,
                'B_critical': B_critical,
                'CTmin_critical': CTmin_critical,
                'CTmax_critical': CTmax_critical,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
                'N_POP': N_POP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'seed': seed,
                'OUTNAME': f"VT_autocorrelated_{seed}"
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
    params_unique['OUTNAME'] = "VT_autocorrelated"
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)

def kentucky():
    '''
    Use KY NASA POWER, repeat 5 times with different seeds
    '''
    param_filename = 'KY_params.csv'
    param_unique_filename = 'KY_params_unique.csv'


    # List of params to scan
    seed_list = range(5)
    # OUTNAME will reflect the change of these parameters

    # List of parameters to change from default values, but keep constant across all simulations
    # cycle through data from 1981-1-1 to 1986-12-31, 200 times
    NUM_DAYS_TO_REPEAT = 2191
    NUM_REP_TEMP_DATA = 200
    MU = 1e-6
    FIXED_GEN_LEN = 21
    GEN_LEN_DEPENDS_ON_TEMP = 'F'
    B_default = 30
    CTmin_default = 0
    B_critical = 30
    CTmin_critical = 1.5
    CTmax_critical = 40

    BURNIN = 5000
    STDEV_TEMP = 0
    N_POP = 5000
    TEMPDATA_PATH = "./KY_timeseries.csv"
    OUTDIR = "/projects/lotterhos/TPC_evol_SLiM"
 
    # Other params will use values from params_default

    # Loop through all combinations of parameters to scan
    # For each combination, create a new parameter dictionary, add it to the parameter list
    params_list = []
    for i, seed in enumerate(seed_list):
        new_row = {
                'NUM_DAYS_TO_REPEAT': NUM_DAYS_TO_REPEAT,
                'NUM_REP_TEMP_DATA': NUM_REP_TEMP_DATA,
                'MU': MU,
                'FIXED_GEN_LEN': FIXED_GEN_LEN,
                'GEN_LEN_DEPENDS_ON_TEMP': GEN_LEN_DEPENDS_ON_TEMP,
                'B_default': B_default,
                'CTmin_default': CTmin_default,
                'B_critical': B_critical,
                'CTmin_critical': CTmin_critical,
                'CTmax_critical': CTmax_critical,
                'BURNIN': BURNIN,
                'STDEV_TEMP': STDEV_TEMP,
                'N_POP': N_POP,
                'TEMPDATA_PATH': TEMPDATA_PATH,
                'OUTDIR': OUTDIR,
                'seed': seed,
                'OUTNAME': f"KY_{seed}"
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
    params_unique['OUTNAME'] = "KY"
    # Save as csv file
    params_unique.to_csv(param_unique_filename, index=False)       

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare simulation parameters')
    parser.add_argument('--task', type=str, required=True,
                       choices=['gaussian', 'gaussian2', 'gaussian_alt_initial', 
                       'temp_trop', 'two_normal', 'include_sd_pop', 'sine', 'sine2', 'sine3', 'sine4',
                       'sine_test', 'vermont', 'kentucky'],
                       help='Type of simulation task')
    
    args = parser.parse_args()
    if args.task == 'gaussian':
        print("making parameter files for gaussian task.")
        gaussian()
    elif args.task == 'gaussian2':
        print("making parameter files for gaussian2 task.")
        gaussian2()
    elif args.task == 'gaussian_alt_initial':
        print("making parameter files for gaussian task with alternative default B and CTmin.")
        gaussian_alt_initial()
    elif args.task == 'temp_trop':
        print("making parameter files for temperate vs. tropical with different population sizes.")
        temp_trop()
    elif args.task == 'two_normal':
        print("making parameter files for two normal distributions task.")
        two_normal()
    elif args.task == 'include_sd_pop':
        print("making parameter files for including sd_pop")
        include_sd_pop()
    elif args.task == 'sine':
        print("making parameter files for sine task.")
        sine()
    elif args.task == 'sine2':
        print("making parameter files for sine2 task.")
        sine2()
    elif args.task == 'sine3':
        print("making parameter files for sine3 task.")
        sine3()
    elif args.task == 'sine4':
        print("making parameter files for sine4 task.")
        sine4()
    elif args.task == 'sine_test':
        print("making parameter files for sine (test) task.")
        sine_test()
    elif args.task == 'vermont':
        print("making parameter files for vermont task.")
        vermont()
    elif args.task == 'kentucky':
        print("making parameter files for kentucky task.")
        kentucky()
