import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import glob
import os

# modify path for your task of choice
params_unique_path = "./01_prepare_input_parameters/gaussian_params_unique.csv"
params_unique = pd.read_csv(params_unique_path)

# Load full params to match replicates
params_path = "./01_prepare_input_parameters/gaussian_params.csv"
params = pd.read_csv(params_path)

# Column titles to extract and plot
titles = ['day', 'Temp', 'B_mean', 'CTmin_mean', 'CTmax_mean', 'Topt_mean', 'B_CTmin_cov', 'fitness_mean']

rbw_cmap = plt.get_cmap('rainbow')
plt.rcParams.update({'font.size': 10})


def get_matching_params(unique_row, params_df):
    """Get all param rows matching a unique_row (all replicates)."""
    merge_cols = [col for col in unique_row.index if col in params_df.columns and col not in ['seed', 'OUTNAME']]
    row_df = unique_row.to_frame().T
    return params_df.merge(row_df[merge_cols], on=merge_cols, how='inner')


# Iterate through each unique parameter combination
for idx, unique_row in params_unique.iterrows():
    OUTDIR = unique_row['OUTDIR']
    OUTNAME = unique_row['OUTNAME']
    RUNTIME = unique_row['RUNTIME']
    
    print(f"Processing parameter set: {OUTNAME}")
    
    # Get all matching replicate rows
    replicates = get_matching_params(unique_row, params)
    # Create figure with 2x4 subplots (8 total)
    fig, ax = plt.subplots(2, 4, figsize=(20, 10))
    data_list = []
    n_complete = 0
    
    # Loop through all replicates (different seeds)
    for rep_idx, rep_row in replicates.iterrows():
        seed = rep_row['seed']
        rep_outname = rep_row['OUTNAME']
        
        # Check if .trees file exists (indicates successful completion)
        trees_file = f"{OUTDIR}/{rep_outname}.trees"
        txt_file = f"{OUTDIR}/{rep_outname}.txt"
        
        if not os.path.exists(trees_file):
            print(f"  Trees file not found (simulation didn't complete): {trees_file}")
            continue
        
        if not os.path.exists(txt_file):
            print(f"  Text file not found: {txt_file}")
            continue
        
        print(f"  Loading: {txt_file}")
        
        try:
            # Load data using pandas to access columns by name
            data = pd.read_csv(txt_file)
            
            # Check that all required columns exist
            missing_cols = [col for col in titles if col not in data.columns]
            if missing_cols:
                print(f"  Missing columns {missing_cols} in {txt_file}")
                continue
            
            data_list.append(data)
            n_complete += 1
            
            # Plot each replicate
            for i, title in enumerate(titles):
                ax.flat[i].plot(data['cycle'], data[title], 
                               color=rbw_cmap(rep_idx / len(replicates)), 
                               linewidth=0.2)
                ax.flat[i].set_title(title)
                ax.flat[i].set_xlabel("generation")
        
        except Exception as e:
            print(f"  Error loading {txt_file}: {e}")
            continue
    
    # Check if we have any complete simulations
    if len(data_list) == 0:
        print(f"No complete simulations for {OUTNAME}, skipping...")
        plt.close(fig)
        continue
    
    print(f"  {n_complete} complete simulations found")
    
    # Calculate average across replicates
    # Create average dataframe
    avg_df_dict = {'generation': data_list[0]['cycle'].values}
    end_df = {}
    
    for title in titles:
        # Stack all replicate data for this column
        all_values = np.array([df[title].values for df in data_list])
        
        # Calculate mean across replicates
        avg_values = np.mean(all_values, axis=0)
        avg_df_dict[title] = avg_values
        
        # Get end values from each replicate
        end_df[title] = [df[title].iloc[-1] for df in data_list]
    
    # Plot the averages
    for i, title in enumerate(titles):
        ax.flat[i].plot(avg_df_dict['generation'], avg_df_dict[title], 
                       linewidth=2, color='black')
    
    # Save figure and data using OUTNAME from params_unique
    fig.tight_layout()
    fig.savefig(f"{OUTDIR}/summary_{OUTNAME}.png")
    np.save(f"{OUTDIR}/avg_df_{OUTNAME}.npy", avg_df_dict)
    np.save(f"{OUTDIR}/end_df_{OUTNAME}.npy", end_df)
    
    plt.close(fig)
    print(f"  Saved: summary_Fig_{OUTNAME}.png, avg_df_{OUTNAME}.npy, and end_df_{OUTNAME}.npy")

print(f"Finished processing all log files.")
