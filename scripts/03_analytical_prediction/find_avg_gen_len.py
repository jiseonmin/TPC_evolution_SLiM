import glob
import pandas as pd
import sys

# Find a file that matches OUTPATH and OUTNAME pattern
def find_avg_gen_len(OUTDIR, OUTNAME):
    logs = glob.glob(f"{OUTDIR}/{OUTNAME}*.txt")

    # Read first log found
    log = pd.read_csv(logs[0])

    # Total days between start to the end of log files divided by the number of gens = avg generation length
    # Round it to the closest integer
    days = list(log['day'])
    gens = list(log['cycle'])
    avg_gen_len = round((days[-1] - days[0]) / (gens[-1] - gens[0]))

    return avg_gen_len

if __name__=="__main__":
    OUTDIR = sys.argv[1]
    OUTNAME = sys.argv[2]
   
    print(find_avg_gen_len(OUTDIR, OUTNAME))
