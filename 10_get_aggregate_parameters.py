import pandas as pd

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



if __name__ == "__main__":
    
    
    df = pd.read_csv(sys.argv[1])
    
    # new columns
    df["dur_over_amp"] = df.dur / df.ampl_rec
    df["amp_over_ed_rec"] = df.ampl_rec / df.ed_rec
    df["dur_over_ed_rec"] = df.ampl_rec / df.ed_rec
    
    dfsort = df.sort_values(by="tstart", ascending=True)
    group = dfsort.groupby(["starid"])
    res = pd.DataFrame()
    
    # count flares
    res["nflares"] = group.tstart.count()
    
    
    for col in ["ed_rec", "ampl_rec","dur","dur_over_amp","dur_over_ed_rec", "amp_over_ed_rec"]:
    
        print(f"\nTreat {col}:\n")

        print("Do basic stats")
        res = res.join(basic_stats(group, col))

        print("Do differential stats step size 1.")
        res = res.join(basic_diff_stats(group, col, 1))

        print("Do differential stats step size 2.")
        res = res.join(basic_diff_stats(group, col, 2))

        print("Do differential stats step size 3.")
        res = res.join(basic_diff_stats(group, col,3))

    
    print("Calculated parameters. Aggregate over 200 light curves.")
    agg = res.groupby(pd.cut(df["midlat_deg"], np.linspace(0, 90, res.shape[0]//200))).mean()
    
    print("Save to file")
    res.to_csv(sys.argv[2])