""" 
Python 3.8 -- UTF-8

Ekaterina Ilin 
MIT License (2022)

Statistics module. 
Contains function to calculate statistics about flaring ensembles.
"""

import numpy as np
import pandas as pd



def calibratable_diff_stats(df, group, col, steps, size=200):
    """Calculate statistics about flare parameter col that are 
    independent of the flare distribution and only concerned with
    the timing.
    
    Parameters:
    ------------
    df : pd.DataFrame
        full flare table
    group : pd.df
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
    se["ed_rec"] = df["ed_rec"]
    

    av_rec_num_flares = int(np.rint(se.groupby("midlat_deg").ed_rec.count().mean()))
    
    # cut dataframe into groups with similar mid latitude but random inclinations
    cut, bins = pd.cut(se["midlat_deg"],
                       np.linspace(se["midlat_deg"].min(),
                                   se["midlat_deg"].max(), 
                                   se.shape[0] // size // av_rec_num_flares),
                       retbins=True)
    
    agg = se.groupby(cut)
    
    k = agg.apply(lambda x: x[col].median())
    
    s = agg.apply(lambda x: x[col].mean())

    sm = agg.apply(lambda x: x[col].std())
    
    nflares = agg["ed_rec"].count()
    
    nstars = agg.apply(lambda x: x["midlat_deg"].drop_duplicates().count())
 
    # define column names and return DataFrame
    listofsuffixes = ['median', 'mean', 'std', 'nflares','nstars',]
    list_of_colnames = [f"diff_{col}_{suf}_stepsize{steps}" for suf in listofsuffixes]
    
    return pd.DataFrame(dict(zip(list_of_colnames, [k, s, sm, nflares, nstars]))), bins
	

    
    