import pandas as pd
import numpy as np
import sys

import time

from flares.stats import calibratable_diff_stats


if __name__ == "__main__":
    
    # read flare table
    df = pd.read_csv(sys.argv[1])

    # use only relevant columns to save time
    df = df[["tstart","starid","midlat_deg","ed_rec"]]
    
    # sort tstart in ascending order for waiting time distribution calculations
    dfsort = df.sort_values(by="tstart", ascending=True)
    
    # grouping by ID and mid-latitude separates individual light curves
    group = dfsort.groupby(["starid","midlat_deg"])

    #size of ensemble
    size = 400
    
    # calculate aggregate statistics with different lags, i.e. step sizes
    print("Do calibratable stats step size 1.")
    res, bins = calibratable_diff_stats(dfsort, group, 'tstart', 1, size=size)
#     print(res.head())
#     print("Do calibratable stats step size 2.")
#     res = pd.concat([res, calibratable_diff_stats(dfsort, group, 'tstart', 2, size=size)[0]],
#                     axis=0)

#     print("Do calibratable stats step size 3.")
#     res = pd.concat([res, calibratable_diff_stats(dfsort, group, 'tstart', 3, size=size)[0]],
#                     axis=0)    
    
#     res = res.reset_index()

    # calculate mid-/min-/max-/width of latitudes of ensembles of lcs
    print(res.head(), res.index)
    res["minlat"] = [l.left for l in res.index.values]
    res["maxlat"] = [l.right for l in res.index.values]
    res["latwidth"] = res.maxlat - res.minlat
    res["midlat2"] = (res.maxlat + res.minlat)/2.
    res["size"] = size
    
    print("Save to file")
    res.to_csv(sys.argv[2])
