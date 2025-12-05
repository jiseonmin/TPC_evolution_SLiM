# Make expected fitness landscape, optimal B and CTmin (peak of landscape),
# and expected path to the optimum from initial state
import numpy as np
from tpc_functions_oo import *
import scipy
import sys
import os

RECOVERY = sys.argv[1] # string either T or F
AVG_GEN_LEN = int(sys.argv[2])
MEAN_TEMP = float(sys.argv[3]) 
STDEV_TEMP = float(sys.argv[4])
B_default = float(sys.argv[5]) 
CTmin_default = float(sys.argv[6])
B_critical = float(sys.argv[7])
DeltaB = float(sys.argv[8])
CTmin_critical = float(sys.argv[9])
DeltaCTmin = float(sys.argv[10])
CTmax_critical = float(sys.argv[11]) 
DeltaCTmax = float(sys.argv[12])
OUTDIR = sys.argv[13]
OUTNAME = sys.argv[14]


# Initiate a tpc object
tpc = tpc_functions(B_critical = B_critical,
                    Delta_B = DeltaB, 
                    CTmin_critical = CTmin_critical,
                    Delta_CTmin = DeltaCTmin,
                    CTmax_critical = CTmax_critical,
                    Delta_CTmax = DeltaCTmax,
                    num_days_per_gen = AVG_GEN_LEN)

## 1. Find expected fitness landscape with given temperature distribution (Gaussian)

CTmin_list = np.linspace(-5, 40, 450)
B_list = np.linspace(1e-3, 40, 300)
[CTmin_grid, B_grid] = np.meshgrid(CTmin_list, B_list)
CTmax_grid = CTmin_grid + B_grid
if STDEV_TEMP < np.nextafter(0, 1):
    # (using nextafter to check if sigmaT is zero since it is always a float)
    # if T is constant, use a fitness function without integration over T to save time.
    meanWcontour = tpc.w_TPC(CTmin=CTmin_list, 
                            B=B_list,
                            T=MEAN_TEMP)
else:
    if RECOVERY == 'F':
        meanWcontour = tpc.expected_w_TPC_no_recovery(muT=MEAN_TEMP, 
                                                    sigmaT=STDEV_TEMP,
                                                    CTmin=CTmin_list,
                                                    B=B_list)
    elif RECOVERY == 'T':
        meanWcontour = tpc.expected_w_TPC_recovery(B=B_list, 
                                                   CTmin=CTmin_list,
                                                   muT=MEAN_TEMP,
                                                   sigmaT=STDEV_TEMP)
    else:
        print("invalid RECOVERY input. It should be either T or F")

print("contour made")

## 2. Find where fitness is maximized on the landscape
max_idx = np.unravel_index(np.argmax(meanWcontour), np.shape(meanWcontour))
CTmin0 = CTmin_grid[max_idx]
B0 = B_grid[max_idx]
if STDEV_TEMP < np.nextafter(0,1):
    print("standard deviation of temperature too small, returning maximum found from the contour plot")
    CTmin_opt = CTmin0
    B_opt = B0
else:
    if RECOVERY == 'F':
        CTmin_opt, B_opt = tpc.optimize_expected_w_TPC_no_recovery(
                                muT=MEAN_TEMP,
                                sigmaT=STDEV_TEMP,
                                CTmin0=CTmin0,
                                B0=B0
                               )
    else:
        CTmin_opt, B_opt = tpc.optimize_expected_w_TPC_recovery(
                                muT=MEAN_TEMP,
                                sigmaT=STDEV_TEMP,
                                CTmin0=CTmin0,
                                B0=B0
                                )
print("optimal B and CTmin found")

# 3. Find theoretical trajectory from initial B and CTmin to the optimal B and CTmin (numerical solution to initial value problem)
if STDEV_TEMP < np.nextafter(0, 1):
    print("standard deviation of temperature too small. Using ODE for fixed temperature.")
    sol = tpc.CTmin_B_traj_fixed_T(
                                    CTmin0=CTmin_default,
                                    B0=B_default,
                                    T=MEAN_TEMP
            )
else:
    if RECOVERY == 'F':
        sol = tpc.expected_CTmin_B_traj_no_recovery(CTmin0=CTmin_default,
                                                B0=B_default,
                                                muT=MEAN_TEMP,
                                                sigmaT=STDEV_TEMP
                                                )
    else:
        sol = tpc.expected_CTmin_B_traj_recovery(CTmin0=CTmin_default,
                                                 B0=B_default,
                                                 muT=MEAN_TEMP,
                                                 sigmaT=STDEV_TEMP
                                                 )

print("theoretical trajectory calculated.")
np.savez(f"{OUTDIR}{OUTNAME}_analytical_info.npz", 
         CTmin_grid=CTmin_grid, 
         B_grid=B_grid, 
         W_contour=meanWcontour, 
         CTmin_opt=CTmin_opt, 
         B_opt=B_opt, 
         sol=sol)
