import pandas as pd
import numpy as np
import sys

import time

from flares.stats import calibratable_diff_stats


if __name__ == "__main__":
    
    # read flare table
    df = pd.read_csv(sys.argv[1])

    # use only relevant columns to save time
    df = df[["tstart","starid","midlat_deg"]]
    
    # sort tstart in ascending order for waiting time distribution calculations
    dfsort = df.sort_values(by="tstart", ascending=True)
    
    # grouping by ID and mid-latitude separates individual light curves
    group = dfsort.groupby(["starid","midlat_deg"])
    
    # calculate aggregate statistics with different lags, i.e. step sizes
    print("Do calibratable stats step size 1.")
    res, bins = calibratable_diff_stats(group, 'tstart', 1)

    print("Do calibratable stats step size 2.")
    res = res.join(calibratable_diff_stats(group, 'tstart', 2)[0])

    print("Do calibratable stats step size 3.")
    res = res.join(calibratable_diff_stats(group, 'tstart', 3)[0])    
    
    # calculate mid-/min-/max-/width of latitudes of ensembles of lcs
    res["midlat2"] = (bins[:-1] + bins[1:]) / 2.
    res["minlat"] = bins[:-1]
    res["maxlat"] = bins[1:]
    res["latwidth"] = bins[1:] - bins[:-1] 
    
    print("Save to file")
    res.to_csv(sys.argv[2])
