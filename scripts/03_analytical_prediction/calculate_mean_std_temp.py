import pandas as pd
import sys

# tempdata path is relative to slim folder, so add it to sys.path
sys.path.insert(1, '../../slim')

tempdata_path = sys.argv[1]
tempdata = pd.read_csv(tempdata_path)

# get mean and standara deviation of 'T2M' column
mean_temp = tempdata.T2M.mean()
std_temp = tempdata.T2M.std()
print(f"{mean_temp} {std_temp}")