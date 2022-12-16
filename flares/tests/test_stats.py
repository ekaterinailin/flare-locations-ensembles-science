import pytest
import numpy as np
import pandas as pd

import os

from ..stats import calibratable_diff_stats

def test_calibratable_diff_stats():
    """Test two random data sets """
    
    # generate fake large dataset
    N = 800 # total number of flares we deal with
    size = 4 # number of ensembles to generate
    df = pd.DataFrame({"COL":np.random.choice(np.arange(10), size=N),
                       "col4":np.random.choice(np.arange(100), size=N),
                       "col0":np.random.choice(np.arange(10), size=N),
                       "col1":np.random.normal(30, 1, N),
                       "midlat_deg":np.random.choice(np.arange(20)*4, size=N),
                       "ed_rec":np.random.normal(30, 1, N),
                       "tstart":np.random.rand(N) * 100})

    # sort times
    df = df.sort_values("tstart")

    # group by two columns
    group = df.groupby(["col0","midlat_deg"])

    print(group.count())
    # apply the function
    dd, bins = calibratable_diff_stats(df, group, "tstart", 1, size=size)
    print(dd)
    # assert shape comes out  correct
    assert dd.shape == (4,5)
    
    # all values should be positive if the data are sorted
    assert (dd > 0).all().all()

    # check if columns are correct
    assert (dd.columns.values == ["diff_tstart_median_stepsize1",
                                  "diff_tstart_mean_stepsize1",
                                  "diff_tstart_std_stepsize1",
                                  "diff_tstart_nflares_stepsize1",
                                  "diff_tstart_nstars_stepsize1",
                                  ]).all()

    # apply the function with stepsize 2
    group = df.groupby(["col0","midlat_deg"])
    dd, bins = calibratable_diff_stats(df, group, "tstart", 2, size=size)

    # rerun the checks from before 
    # assert shape comes out  correct
    assert dd.shape == (4,5)
    assert bins.shape[0] == size + 1
    # all values should be positive if the data are sorted
    assert (dd > 0).all().all()
    # check if columns are correct
    assert (dd.columns.values == ["diff_tstart_median_stepsize2",
                                  "diff_tstart_mean_stepsize2",
                                  "diff_tstart_std_stepsize2",
                                  "diff_tstart_nflares_stepsize2",
                                  "diff_tstart_nstars_stepsize2",
                                  ]).all()

