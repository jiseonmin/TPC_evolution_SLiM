import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
params_df = pd.read_csv("./01_prepare_params_df/gaussian_params_unique.csv")

# Todo - update titles (more columns added to log files
# Use iterrow to go through all rows of params_df (don't need muTlist, and other lists), find all file that matches {OUTDIR}{OUTNAME}_seed_*.trees pattern
# load txt file with the same title as the .trees file. This will replace the step checking whether population crashed. (.trees only saved if simulation didn't crash)
# Finally, save files using the row's OUTDIR and OUTNAME (no need to remove _seed_0)
# Remove ax.flat[i].vlines because the log file only starts recording after burnin period now
# Plot only 8 columns (days, Temp, B_mean, CTmin_mean, CTmax_mean, Topt_mean, B_CTmin_cov, fitness_mean) 
muTlist = set(params_df['muT'])
sigmaTlist = set(params_df['sigmaT'])
seedlist = set(params_df['seed'])
runtime = params_df['RUNTIME'][0]
outdir = "/projects/lotterhos/TPC_sim_results/data"
titles = ['mean(B)', 'sd(B)', 'mean(CTmin)', 'sd(CTmin)', 'cov(B, CTmin)', 'mean(fitness)', 'sd(fitness)', 'mean(T)', 'sd(T)']
rbw_cmap = plt.get_cmap('rainbow')
plt.rcParams.update({'font.size': 10})


for muT in muTlist:
    for sigmaT in sigmaTlist:
        print(f"collect files with muT={muT}, sigmaT={sigmaT}")
        fig, ax = plt.subplots(3, 3, figsize=(15, 15))
        data_list = []
        n_complete = 0
        for seed in seedlist:
            outname = params_df[(params_df['muT']==muT) & (params_df['sigmaT']==sigmaT) & (params_df['seed']==seed)]['OUTNAME'].iloc[0]
            filename = f"{outdir}/{outname}.txt"
            print(filename)
            data = np.loadtxt(filename, delimiter=',', skiprows=1)
            if data[-1, 0] < runtime + 1:
                "population crashed after burnin"
            else:
                data_list.append(data)
                n_complete += 1
            for i, title in enumerate(titles):
                # zeroth entry = generation
                ax.flat[i].plot(data[:,0], data[:,i+2], color=rbw_cmap(seed/len(seedlist)), linewidth=0.2)
                ax.flat[i].set_title(title)
                ax.flat[i].set_xlabel("generation")
                # mark where burn in ends (5000 gen)
                ax.flat[i].vlines(5000, ymin=min(data[:,i+2]), ymax=max(data[:,i+2]), linestyle='--', color='grey')
        if len(data_list) == 0:
            print(f"No complete simulation for muT={muT}, sigmaT={sigmaT}, skipping...")
            plt.close(fig)
            continue
        
        avg_data = sum(data_list) / len(data_list)

        # make dictionary of data
        avg_df = {'cycle': avg_data[:, 0]}
        end_df = {}
        for i, title in enumerate(titles):
            ax.flat[i].plot(avg_data[:,0], avg_data[:,i+2], linewidth = 2, color='black')
            avg_df[title] = avg_data[:, i+2]
            end_df[title] = [data_list[j][-1, i+2] for j in range(n_complete)]

        eg_outname = params_df[(params_df['muT']==muT) & (params_df['sigmaT']==sigmaT) & (params_df['seed']==0)]['OUTNAME'].iloc[0]
        fig.savefig(f"{outdir}/SI_Fig_{eg_outname.replace("_seed_0", "")}.png")
        np.save(f"{outdir}/avg_df_{eg_outname.replace("_seed_0", "")}.npy", avg_df)
        np.save(f"{outdir}/end_df_{eg_outname.replace("_seed_0", "")}.npy", end_df)


print(f"Finished processing log files.")
