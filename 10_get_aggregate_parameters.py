import pandas as pd
import numpy as np
import sys

import time



def basic_stats(group, col):
    """Calculate basic statistic about flare parameter col.
    
    Parameters:
    ------------
    group : pd.DataFrameGroupBy
        grouped table, where each group is a list of 
        flares from one light curve
    col : str
        column of grouped table with a flare parameter
        
    Return:
    -------
    mean, median, std, min and max of parameter under col,
    put together in a DataFrame with group index
    """
    x = group[col]

    listofsuffixes = ['mean', 'median', 'std', 'min', 'max']
    res = [x.mean(), x.median(), x.std(), x.min(), x.max()]
    
    return pd.DataFrame(dict(zip([f"{col}_{suf}" for suf in listofsuffixes],res)))

def basic_diff_stats(group, col, steps):
    """Calculate basic statistic about flare parameter col.
    
    Parameters:
    ------------
    group : pd.DataFrameGroupBy
        grouped table, where each group is a list of 
        flares from one light curve, sorted by time
    col : str
        column of grouped table with a flare parameter
    steps : int
        step size of difference calculation
        
    Return:
    -------
    mean, median, std, min and max of parameter under col
    """
    se = group[col]
    
    listofsuffixes = ['mean', 'median', 'std', 'min', 'max']
    res = [se.apply(lambda x: x.diff(periods=steps).mean()),
           se.apply(lambda x: x.diff(periods=steps).median()),
           se.apply(lambda x: x.diff(periods=steps).std()),
           se.apply(lambda x: x.diff(periods=steps).min()),
           se.apply(lambda x: x.diff(periods=steps).max()),]
    
    return pd.DataFrame(dict(zip([f"diff_{col}_{suf}_stepsize{steps}" for suf in listofsuffixes],res)))



def calibratable_diff_stats(group, col, steps):
    """Calculate statistics about flare parameter col that are 
    independent of the flare distribution and only concerned with
    the timing.
    
    Parameters:
    ------------
    group : pd.DataFrameGroupBy
        grouped table, where each group is a list of 
        flares from one light curve, sorted by time
    col : str
        column of grouped table with a flare parameter
    steps : int
        step size of difference calculation
        
    Return:
    -------
    mean, median, std, min and max of parameter under col
    """
    # calculate waiting times
    se = group.apply(lambda x: x[col].diff(periods=steps)).reset_index()
    
    # delete superfluos index
    del se["level_2"]
    
    # cut dataframe into groups with similar mid latitude but random inclinations
    cut, bins = pd.cut(se["midlat_deg"], np.linspace(0, 90, se.shape[0]//200), retbins=True)
    agg = se.groupby(cut)
    
    # Calculate kurtosis of group
    k = agg.apply(lambda x: x.kurtosis())["tstart"]
    
    # Calculate skewness of group
    s = agg.apply(lambda x: x.skew())["tstart"]
    
    # Calculate std/over mean of group
    sm = agg.apply(lambda x: x.std()/x.mean())["tstart"]
    
    # 
    listofsuffixes = ['kurtosis', 'skew', 'std_over_mean']
    list_of_colnames = [f"diff_{col}_{suf}_stepsize{steps}" for suf in listofsuffixes]
    return pd.DataFrame(dict(zip(list_of_colnames, [k, s, sm]))), bins




if __name__ == "__main__":
    
    
    df = pd.read_csv(sys.argv[1])#, names=['istart','istop','tstart','tstop','ed_rec','ed_rec_err','ampl_rec','dur','total_n_valid_data_points','midlat_deg','inclination_deg','n_spots','beta_1','beta_2','beta_3','alpha_1','alpha_2','alpha_3','lons_1','lons_2','lons_3','starid'])
    
    # new columns
#     df["dur_over_amp"] = df.dur / df.ampl_rec
#     df["amp_over_ed_rec"] = df.ampl_rec / df.ed_rec
#     df["dur_over_ed_rec"] = df.ampl_rec / df.ed_rec
    df = df[["tstart","starid","midlat_deg"]]
    dfsort = df.sort_values(by="tstart", ascending=True)
    group = dfsort.groupby(["starid","midlat_deg"])
    
    # count flares 
    start_time = time.time()
#     res["nflares"] = group.tstart.count()
#     print("--- %s seconds ---" % (time.time() - start_time))
    
#     for col in ["ed_rec", "ampl_rec","dur","dur_over_amp","dur_over_ed_rec", "amp_over_ed_rec"]:
    
#         print(f"\nTreat {col}:\n")

#         print("Do basic stats")
#         res = res.join(basic_stats(group, col))
#         print("--- %s seconds ---" % (time.time() - start_time))

#         print("Do differential stats step size 1.")
#         res = res.join(basic_diff_stats(group, col, 1))
#         print("--- %s seconds ---" % (time.time() - start_time))

#         print("Do differential stats step size 2.")
#         res = res.join(basic_diff_stats(group, col, 2))
#         print("--- %s seconds ---" % (time.time() - start_time))
        
#         print("Do differential stats step size 3.")
#         res = res.join(basic_diff_stats(group, col,3))
#         print("--- %s seconds ---" % (time.time() - start_time))



    print("Do calibratable stats step size 1.")
    res, bins = calibratable_diff_stats(group, 'tstart', 1)
#     print("--- %s seconds ---" % (time.time() - start_time))
    
    
    
   

    print("Do calibratable stats step size 2.")
    res = res.join(calibratable_diff_stats(group, 'tstart', 2)[0])
#     print("--- %s seconds ---" % (time.time() - start_time))
    
    


    print("Do calibratable stats step size 3.")
    res = res.join(calibratable_diff_stats(group, 'tstart', 3)[0])
#     print("--- %s seconds ---" % (time.time() - start_time))
    
    
    res["midlat2"] = (bins[:-1] + bins[1:]) / 2.
    

#     print("Calculated parameters. Aggregate over 200 light curves.")
#     agg = res.groupby(pd.cut(res["midlat_deg"], np.linspace(0, 90, res.shape[0]//200))).mean()
    
#     print("--- %s seconds ---" % (time.time() - start_time))
    
    print("Save to file")
    res.to_csv(sys.argv[2])
