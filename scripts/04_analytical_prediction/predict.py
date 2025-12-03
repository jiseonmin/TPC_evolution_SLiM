# For a given muT, sigmaT and initial B and CTmin, compute expected fitness landscape, and expected TPC trajectory 
# Premake fitness landscape when there is within-generation fluctuation in temperature, because it takes too long.
import numpy as np
from tpc_functions_oo import *
import scipy
import sys
import os

muT = float(sys.argv[1])
sigmaT = float(sys.argv[2])
B_initial = float(sys.argv[3])
CTmin_initial = float(sys.argv[4])
OUTNAME = sys.argv[5]
datadir = "/projects/lotterhos/TPC_sim_results/data/"
if os.path.isdir(datadir):
    print("working on cluster")
    sys.stdout.flush()
else:
    print("working on local machine")
    sys.stdout.flush()
    datadir = "../SLiM_scripts/data/"

# Initiate a tpc object
tpc = w_TPC()

## 1. Find expected fitness landscape with given temperature distribution (Gaussian)

CTmin_list = np.linspace(-5, 40, 450)
B_list = np.linspace(1e-3, 40, 300)
[CTmin_grid, B_grid] = np.meshgrid(CTmin_list, B_list)
CTmax_grid = CTmin_grid + B_grid
if sigmaT<np.nextafter(0, 1):
    # (using nextafter to check if sigmaT is zero since it is always a float)
    # if T is constant, use a fitness function without integration over T to save time.
    meanWcontour = tpc.w_TPC(CTmin=CTmin_list, 
                            B=B_list,
                            T=muT)
else:
    meanWcontour = tpc.expected_w_TPC_no_recovery(muT=muT, 
                                                    sigmaT=sigmaT,
                                                    CTmin=CTmin_list,
                                                    B=B_list)

print("contour made")

## 2. Find where fitness is maximized on the landscape
max_idx = np.unravel_index(np.argmax(meanWcontour), np.shape(meanWcontour))
CTmin0 = CTmin_grid[max_idx]
B0 = B_grid[max_idx]
if sigmaT<np.nextafter(0,1):
    print("standard deviation too small, returning minimum from the contour plot")
    CTmin_opt = CTmin0
    B_opt = B0
else:
    CTmin_opt, B_opt = tpc.optimize_expected_w_TPC_no_recovery(
                muT=muT,
                sigmaT=sigmaT,
                CTmin0=CTmin0,
                B0=B0
            )
print("optimal B and CTmin found")

# 3. Find theoretical trajectory from initial B and CTmin to the optimal B and CTmin (numerical solution to initial value problem)
if sigmaT < np.nextafter(0, 1):
    print("sigmaT too small. Using ODE for fixed temperature.")
    sol = tpc.CTmin_B_traj_fixed_T(
                                    CTmin0=CTmin_initial,
                                    B0=B_initial,
                                    T=muT
            )
else:
    sol = tpc.expected_CTmin_B_traj_no_recovery(CTmin0=CTmin_initial,
                                                B0=B_initial,
                                                muT=muT,
                                                sigmaT=sigmaT
                                                )

print("theoretical trajectory calculated.")
np.savez(f"{datadir}{OUTNAME}_analytical_info.npz", CTmin_grid=CTmin_grid, B_grid=B_grid, W_contour=meanWcontour, CTmin_opt=CTmin_opt, B_opt=B_opt, sol=sol)
