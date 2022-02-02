import numpy as np
import pandas as pd


def basic_stats(group, col):
    """NOT TESTED
    Calculate basic statistic about flare parameter col.
    
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
    
    return pd.DataFrame(dict(zip([f"{col}_{suf}" for suf in listofsuffixes], res)))


def basic_diff_stats(group, col, steps):
    """NOT TESTED
    Calculate basic statistic about flare parameter col.
    
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



def calibratable_diff_stats(group, col, steps, size=200):
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
    size : int
        size of the ensemble to split the table into
        
    Return:
    -------
    mean, median, std, min and max of parameter under col
    """
    # calculate waiting times
    se = group.apply(lambda x: x[col].diff(periods=steps)).reset_index()
    
    # delete superfluos index
    del se["level_2"]
    
    # cut dataframe into groups with similar mid latitude but random inclinations
    cut, bins = pd.cut(se["midlat_deg"],
                       np.linspace(se["midlat_deg"].min(),
                                   se["midlat_deg"].max(), 
                                   se.shape[0] // size),
                       retbins=True)
    
    agg = se.groupby(cut)
    
    # Calculate kurtosis of group
    k = agg.apply(lambda x: x.kurtosis())[col]
    
    # Calculate skewness of group
    s = agg.apply(lambda x: x.skew())[col]
    
    # Calculate std/over mean of group
    sm = agg.apply(lambda x: x.std() / x.mean())[col]
    
    # define column names and return DataFrame
    listofsuffixes = ['kurtosis', 'skew', 'std_over_mean']
    list_of_colnames = [f"diff_{col}_{suf}_stepsize{steps}" for suf in listofsuffixes]
    return pd.DataFrame(dict(zip(list_of_colnames, [k, s, sm]))), bins

