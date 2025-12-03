## Define a TPC object for analysis

import numpy as np
from scipy import optimize
import scipy
from scipy.integrate import solve_ivp, quad, dblquad

class w_TPC:
    """
    thermal performance curve, incorporating enzymatic and physiological fitness components.
    By default, B, CTmin, T (entry for w_TPC) is not an attribute.
    Parameters for the physiological constraints are the attribute.
    """
    def __init__(self, B_critical=40, Delta_B=2, CTmin_critical=0, Delta_CTmin=2, CTmax_critical=40, Delta_CTmax=0.2, num_days_per_gen=10):
        self.B_critical= B_critical
        self.Delta_B = Delta_B

        self.CTmin_critical = CTmin_critical
        self.Delta_CTmin = Delta_CTmin

        self.CTmax_critical = CTmax_critical
        self.Delta_CTmax = Delta_CTmax

        self.num_days_per_gen = num_days_per_gen
    def w_B(self, B):
        '''
        w_B fitness component constraining B, for a given value(s) of B
        '''
        return scipy.special.expit(-(B - self.B_critical) / self.Delta_B)

    def w_CTmin(self, CTmin):
        '''
        w_CTmin: fitness component constraining CTmin, for a given value(s) of CTmin
        '''
        return scipy.special.expit(-(-CTmin + self.CTmin_critical) / self.Delta_CTmin)

    def w_CTmax(self, CTmax):
        '''
        w_CTmax: fitness component constraining CTmax, for a given value(s) of CTmax.
        '''
        return scipy.special.expit(-(CTmax - self.CTmax_critical) / self.Delta_CTmax)

    def w_enzymatic(self, B, CTmin, T, squeeze=True):
        '''
        enzymatic component with given array or a value of B, CTmin, T
        '''
        CTmin_array = np.array(CTmin, ndmin=1)
        B_array = np.array(B, ndmin=1)
        T_array = np.array(T, ndmin=1)

        CTmin_grid, B_grid, T_grid = np.meshgrid(CTmin_array, B_array, T_array)
        Topt_grid = CTmin_grid + 2 / 3 * B_grid

        # Gaussian part of Deutsch et al. model
        row_left = np.exp(-(3 * (T_grid - CTmin_grid - 2 / 3 * B_grid) / B_grid) ** 2)
        
        # Parabolic part
        row_right = 1 - ((T_grid - CTmin_grid - 2 /3 * B_grid) / (1 / 3 * B_grid)) ** 2

        # Apply conditions: w_enzymatic = row_left if T < Topt, = row_right if T > Topt
        out = row_left * (T_grid <= Topt_grid) + row_right * (T_grid > Topt_grid)
        # Also, w_enzymatic cannot be negative. Replace all negative values with zeros.
        out = out * (out >= 0)
        return np.squeeze(out) if squeeze else out

    def w_TPC(self, B, CTmin, T):
        '''
        w_TPC at a given arrary or a value o B, CTmin, and T.
        '''
        CTmin_array = np.array(CTmin, ndmin=1)
        B_array = np.array(B, ndmin=1)
        T_array = np.array(T, ndmin=1)
        CTmin_grid, B_grid, T_grid = np.meshgrid(CTmin_array, B_array, T_array)
        CTmax_grid = CTmin_grid + B_grid

        w_TPC = (self.w_enzymatic(CTmin=CTmin_array, B=B_array, T=T_array, squeeze=False)
                * self.w_B(B_grid)
                * self.w_CTmin(CTmin_grid)
                * self.w_CTmax(CTmax_grid))
        return np.squeeze(w_TPC)

    def expected_w_TPC_recovery(self, B, CTmin, muT, sigmaT):
        '''
        expected value of w_TPC for a given array or value of B, CTmin, muT (mean of normal distributed T), and sigmaT (standard deivation of T).
        Using recovery model. 
        '''
        CTmin_array = np.array(CTmin, ndmin=1)
        B_array = np.array(B, ndmin=1)
        CTmin_grid, B_grid = np.meshgrid(CTmin_array, B_array)
        CTmax_grid = CTmin_grid + B_grid

        output = np.zeros(CTmin_grid.shape)
        for i in range(output.shape[0]):
            for j in range(output.shape[1]):
                CTmin = CTmin_grid[i,j]
                B = B_grid[i,j]
                CTmax = CTmax_grid[i,j]
                fun = lambda T: self.w_TPC(B=B, CTmin=CTmin, T=T) * scipy.stats.norm.pdf(T, muT, sigmaT)
                meanPn, err = scipy.integrate.quad(fun, CTmin, CTmax)
                output[i,j] = meanPn
        return np.squeeze(output)

    def optimize_expected_w_TPC_recovery(self, muT, sigmaT, CTmin0, B0):
        '''
        Given mean and standard deviation of temperature, return optimal B and CTmin, assuming that the temperature is normal-distributed.
        CTmin0 and B0 are initial guesses
        '''
        # lower bound for B (small positive value)
        B_tiny = 1e-3
        def objective(params):
            CTmin, B = params
            expected_w_TPC_recovery = self.expected_w_TPC_recovery(B = B, CTmin = CTmin, muT = muT, sigmaT = sigmaT)
            return -expected_w_TPC_recovery
        bnds = ((None, None), (B_tiny, None))
        result = optimize.minimize(objective, [CTmin0, B0], method='L-BFGS-B', bounds = bnds)
        return result.x

    def expected_w_TPC_no_recovery(self, muT, sigmaT, CTmin, B):
        '''
        Expected TPC given mean and standard deviation of temperature, assuming reproductive output per day after heat damage is zero (no-recovery model).
        The expected value is derived in the SI of the manuscript. 
        In short, it involves calculating probability that the temperature stays under lethal limit for various number of days.
        '''
        nr = self.num_days_per_gen 

        CTmin_array = np.array(CTmin, ndmin=1)
        B_array = np.array(B, ndmin=1)
        

        CTmin_grid, B_grid = np.meshgrid(CTmin_array, B_array)
        output = np.zeros(CTmin_grid.shape)
        for i in range(output.shape[0]):
            for j in range(output.shape[1]):
                CTmin = CTmin_grid[i,j]
                B = B_grid[i,j]
                CTmax = CTmin + B
                fun = lambda T: self.w_TPC(T=T, CTmin=CTmin, B=B) * scipy.stats.norm.pdf(T, muT, sigmaT)
                integral, err = scipy.integrate.quad(fun, CTmin, CTmax)
                r = scipy.stats.norm.cdf(CTmax, muT, sigmaT)
                if (1 - r) < np.finfo(np.float64).tiny:
                    C = 1
                else:
                    C = (1 - nr * r ** (nr - 1) + (-1 + nr) * r ** nr) / (nr * (1 - r)) + r ** (nr - 1)
                output[i,j] = C * integral
        return output

    def optimize_expected_w_TPC_no_recovery(self, muT, sigmaT, CTmin0, B0):
        '''
        Find optimal CTmin and B that maximize expected w_TPC using no-recovery model.
        CTmin0 and B0 are initial guess
        '''
        B_tiny = 1e-3
        def objective(params):
            CTmin, B = params
            expected_w_TPC = self.expected_w_TPC_no_recovery(muT=muT, sigmaT=sigmaT, B=B, CTmin=CTmin)
            return -expected_w_TPC
        bnds = ((None, None), (B_tiny, None))
        results = optimize.minimize(objective, [CTmin0, B0], method='L-BFGS-B', bounds=bnds)
        return results.x

    #######################################################################
    # Functions for numerically solving ivp
    # PARTIAL DERIVATIVES
    def dw_B_dB(self, B):
        '''
        return partial w_B / partial B
        '''
        return - 1 / self.Delta_B * self.w_B(B) * (1 - self.w_B(B))
    def dw_CTmin_dCTmin(self, CTmin):
        '''
        return partial w_CTmin / partial CTmin
        '''
        return 1 / self.Delta_CTmin * self.w_CTmin(CTmin) * (1 - self.w_CTmin(CTmin))
    def dw_CTmax_dB(self, CTmin, B):
        '''
        return partial w_CTmax / partial B
        '''
        CTmax = CTmin + B
        return -1 / self.Delta_CTmax * self.w_CTmax(CTmax) * (1 - self.w_CTmax(CTmax))
    
    def dw_CTmax_dCTmin(self, CTmin, B):
        '''
        return partial w_CTmax / partial B
        '''
        CTmax = CTmin + B
        return -1 / self.Delta_CTmax * self.w_CTmax(CTmax) * (1 - self.w_CTmax(CTmax))
    
    def dw_enzymatic_dB(self, CTmin, B, T):
        '''
        return partial w_enzymatic / partial B
        '''
        if T <= CTmin + 2/3 * B:
            out = np.exp(-((-2 * B - 3 * CTmin + 3 * T) / B) ** 2) * 6 * (3 * T - 3 * CTmin - 2 * B) * (T - CTmin) / B ** 3
        elif T <= CTmin + B:
            out = 6 * (T - CTmin) * (3 * T - 3 * CTmin - 2 * B) / B ** 3
        else:
            out = 0
        return out

    def dw_enzymatic_dCTmin(self, CTmin, B, T):
        '''
        return partial w_enzymatic / partial CTmin
        '''

        if T <= CTmin + 2/3 * B:
            out = 6 * np.exp(-(3 * T - 3 * CTmin - 2 * B)**2/B**2) * (3 * T - 3 * CTmin - 2 * B) / B ** 2
        elif T <= CTmin + B:
            out = 6 * (3 * T - 3 * CTmin - 2 * B) / B ** 2
        else:
            out = 0
        return out

    def dw_TPC_dB(self, CTmin, B, T):
        '''
        return partial w_TPC / partial B
        '''
        CTmax = CTmin + B
        # Using product rule, pull out w_CTmin, which doesn't depend on B.
        out = (
                self.dw_enzymatic_dB(CTmin=CTmin, B=B, T=T) * self.w_B(B) * self.w_CTmax(CTmax)
                + self.w_enzymatic(CTmin=CTmin, B=B, T=T) * self.dw_B_dB(B) * self.w_CTmax(CTmax)
                + self.w_enzymatic(CTmin=CTmin, B=B, T=T) * self.w_B(B) * self.dw_CTmax_dB(CTmin=CTmin, B=B)
                ) * self.w_CTmin(CTmin)
        return out

    def dw_TPC_dCTmin(self, CTmin, B, T):
        '''
        return partial w_TPC / partial CTmin
        '''
        CTmax = CTmin + B
        # Using product rule, pull out w_B, which doesn't depend on CTmin
        out = (
                self.dw_enzymatic_dCTmin(CTmin=CTmin, B=B, T=T) * self.w_CTmin(CTmin) * self.w_CTmax(CTmax)
                + self.w_enzymatic(CTmin=CTmin, B=B, T=T) * self.dw_CTmin_dCTmin(CTmin) * self.w_CTmax(CTmax)
                + self.w_enzymatic(CTmin=CTmin, B=B, T=T) * self.w_CTmin(CTmin) * self.dw_CTmax_dCTmin(CTmin=CTmin, B=B)
                ) * self.w_B(B)
        return out

    def dexpected_w_TPC_recovery_dB(self, muT, sigmaT, CTmin, B):
        '''
        return partial E[w_TPC] / partial B, using recovery model.
        Simply integrate dw_TPC_dB over normal distribution p(T) = Norm(muT, sigmaT)
        '''
        CTmax = CTmin + B
        def integrand(T):
            return self.dw_TPC_dB(T=T, CTmin=CTmin, B=B) * scipy.stats.norm.pdf(T, loc=muT, scale=sigmaT)
        out = quad(integrand, muT-sigmaT * 5, CTmax)
        return out[0]

    def dexpected_w_TPC_no_recovery_dB(self, muT, sigmaT, CTmin, B):
        '''
        return partial E[w_TPC] / partial B, using no-recovery model.
        Both C and E[w_TPC]_recovery depends on B, so output is  partial C / dB * E[w_TPC]_recovery + C * partial E[w_TPC]_recovery / partial dB.
        '''
        CTmax = CTmin + B
        nr = self.num_days_per_gen
        r = scipy.stats.norm.cdf(CTmax, muT, sigmaT)
        if (1 - r) < np.finfo(np.float64).tiny:
            C = 1
            dC_dB = 1/2 * (nr - 1) * scipy.stats.norm.pdf(CTmax, loc=muT, scale=sigmaT)
        else:
            C = (1 - nr * r ** (nr - 1) + (-1 + nr) * r ** nr) / (nr * (1 - r)) + r ** (nr - 1)
            dC_dB = ((nr - 1) * r ** nr - nr * r ** (nr - 1) + 1) / (nr * (1 - r) ** 2) * scipy.stats.norm.pdf(CTmax, loc=muT, scale=sigmaT)
        output = dC_dB * self.expected_w_TPC_recovery(CTmin=CTmin, B=B, muT=muT, sigmaT=sigmaT) + C * self.dexpected_w_TPC_recovery_dB(CTmin=CTmin, B=B, muT=muT, sigmaT=sigmaT)
        return output

    def dexpected_w_TPC_recovery_dCTmin(self, muT, sigmaT, CTmin, B):
        '''
        return partial E[w_TPC] / partial CTmin for recovery model 
        '''
        CTmax = CTmin + B
        def integrand(T):
            return self.dw_TPC_dCTmin(T=T, CTmin=CTmin, B=B) * scipy.stats.norm.pdf(T, loc=muT, scale=sigmaT)
        out = quad(integrand, muT - sigmaT * 5, CTmax)
        return out[0]

    def dexpected_w_TPC_no_recovery_dCTmin(self, muT, sigmaT, CTmin, B):
        '''
        return partial E[w_TPC] / partial CTmin for no recovery model.
        '''
        CTmax = CTmin + B
        nr = self.num_days_per_gen
        r = scipy.stats.norm.cdf(CTmax, muT, sigmaT)
        if (1 - r) < np.finfo(np.float64).tiny:
            C = 1
            dC_dCTmin = 1/2 * (nr - 1) * scipy.stats.norm.pdf(CTmax, loc=muT, scale=sigmaT)
        else:
            C = (1 - nr * r ** (nr - 1) + (-1 + nr) * r ** nr) / (nr * (1 - r)) + r ** (nr - 1)
            dC_dCTmin = ((nr - 1) * r ** nr - nr * r ** (nr - 1) + 1) / (nr * (1 - r) ** 2) * scipy.stats.norm.pdf(CTmax, loc=muT, scale=sigmaT)
        output = dC_dCTmin * self.expected_w_TPC_recovery(CTmin=CTmin, B=B, muT=muT, sigmaT=sigmaT) + C * self.dexpected_w_TPC_recovery_dCTmin(CTmin=CTmin, B=B, muT=muT, sigmaT=sigmaT)
        return output

    def CTmin_B_traj_fixed_T(self, CTmin0, B0, T, t_end=1e9, method="BDF"):
        '''
        Using scipy's solve_ivp, find the theoretical trajectory of CTmin and B, where initial states are CTmin0, B0.
        Solving for fixed temperature case.
        '''
        def ode(t, z):
            CTmin, B = z
            x = self.dw_TPC_dCTmin(CTmin=CTmin, B=B, T=T)
            y = self.dw_TPC_dB(CTmin=CTmin, B=B, T=T)
            return [x,y]
        sol = solve_ivp(ode, [0, t_end], [CTmin0, B0], method=method, dense_output=True)
        return sol

    def expected_CTmin_B_traj_recovery(self, CTmin0, B0, muT, sigmaT, t_end=1e9, method="BDF"):
        '''
        Numerical solution to the ODE describing expected trajectory of mean CTmin, B, using recovery model.
        CTmin0 : initial value of CTmin
        B0 : initial value of B
        '''
        def ode(t, z):
            CTmin, B = z
            x = self.dexpected_w_TPC_recovery_dCTmin(
                        muT=muT,
                        sigmaT=sigmaT,
                        CTmin=CTmin,
                        B=B
                    )
            y = self.dexpected_w_TPC_recovery_dB(
                        muT=muT,
                        sigmaT=sigmaT,
                        CTmin=CTmin,
                        B=B
                    )
            return [x,y]
        sol = solve_ivp(ode, [0, t_end], [CTmin0, B0], method=method, dense_output=True)
        return sol

    def expected_CTmin_B_traj_no_recovery(self, CTmin0, B0, muT, sigmaT, t_end=1e9, method='BDF'):
        '''
        Numerical solution to the ODE describing the expected trajectory of mean CTmin, B, using no recovery model.
        CTmin0 : initial value of CTmin
        B0 : initial value of B
        '''
        def ode(t, z):
            CTmin, B = z
            x = self.dexpected_w_TPC_no_recovery_dCTmin(
                        muT=muT,
                        sigmaT=sigmaT,
                        CTmin=CTmin,
                        B=B
                    )
            y = self.dexpected_w_TPC_no_recovery_dB(
                        muT=muT,
                        sigmaT=sigmaT,
                        CTmin=CTmin,
                        B=B
                    )
            return [x,y]
        sol = solve_ivp(ode, [0, t_end], [CTmin0, B0], method=method, dense_output=True)
        return sol


    
