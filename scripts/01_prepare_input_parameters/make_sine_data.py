import numpy as np

# Create a synthetic data for sine task
mean = 17.5
amplitude = 17.5
period = 360 # in days

days = np.arange(period * 10)
Temp = np.sin(2 * np.pi * days / period) * amplitude + mean
np.savetxt('../../slim/sine.csv', X=Temp, header='T2M', comments="", delimiter=",")