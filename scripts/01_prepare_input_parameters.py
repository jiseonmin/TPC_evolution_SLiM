import argparse
import csv
import itertools

def gaussian_temp():
    '''
    Assume temperature is Gaussian-distributed.
    Use 3 different mean temperatures, 3 different standard deviations, and repeat for 30 different random seeds.
    Simulation data from this pipeline were used to examine generalist-specialist tradeoff in Min et al. manuscript.
    '''
    # Scan both muT and sigmaT to compare low/high fluctuation for A1 - specialist vs. generalist
    muTlist = [5, 20, 35]
    sigmaTlist = [1, 3, 10]
    seedlist = range(30)
    RUNTIME = 20_000
    N=5000
    B_WT = 31
    CTmin_WT = 5

    filename = "A1_nr_params.csv"
    runs = []
    for i, (muT, sigmaT, seed) in enumerate(itertools.product(muTlist, sigmaTlist, seedlist)):
        if (muT == 35) & (sigmaT == 3):
            # needs extra runtime to equilibrate
            runtime = 40_000
        else:
            runtime = RUNTIME
        runs.append({
            'run_id':i,
            'muT':muT,
            'sigmaT':sigmaT,
            'seed':seed,
            'N':N,
            'RUNTIME':runtime,
            'B_WT':B_WT,
            'CTmin_WT':CTmin_WT,
            'OUTNAME':f'A1_nr_muT_{muT}_sigmaT_{sigmaT}_seed_{seed}'
            })
    fieldnames = list(runs[0].keys())
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        writer.writerows(runs)
    print(f"Total number of sims={len(muTlist) * len(sigmaTlist) * len(seedlist)}")

    filename_unique = "A1_nr_params_unique.csv"
    runs_unique = []
    for i, (muT, sigmaT) in enumerate(itertools.product(muTlist, sigmaTlist)):
        if (muT == 35) & (sigmaT == 3):
            runtime = 40_000
        else:
            runtime = RUNTIME
        runs_unique.append({
            'muT': muT,
            'sigmaT': sigmaT,
            'N': N,
            'RUNTIME': runtime,
            'B_WT': B_WT,
            'CTmin_WT': CTmin_WT,
            'OUTNAME': f'A1_nr_muT_{muT}_sigmaT_{sigmaT}'  # No seed in filename
        })
    fieldnames = list(runs_unique[0].keys())
    with open(filename_unique, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
        writer.writeheader()
        writer.writerows(runs_unique)

    print(f"Created {filename_unique} with {len(runs_unique)} rows")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prepare simulation parameters')
    parser.add_argument('--task', type=str, required=True,
                       choices=['gaussian'],
                       help='Type of simulation scenario')
    
    args = parser.parse_args()
    if args.task == 'gaussian':
        gaussian_temp()
