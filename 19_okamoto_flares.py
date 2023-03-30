"""
Python 3.8 -- UTF-8

Ekaterina Ilin, 2023, MIT License

Script that calculate the mean and standard deviation of the flare
waiting time distribution for solar type stars from the flare list
from Okamoto et al. 2021. 

Produces a table with the mean and standard deviation, number of stars
and flares in each subsample, and the range of rotation periods
"""


import pandas as pd
import numpy as np
from astropy.io import fits

import warnings
warnings.filterwarnings('ignore')


def tex_one_err(val, err, r=2):
    """Convert a value and one error into a LaTeX string.

    Parameters
    ----------
    val : float
        The value.
    err : float
        The error.
    r : int, optional
        The number of decimal places to round to, by default 3

    Returns
    -------
    str
        The LaTeX string.
    """

    return ("$" +
            str(np.round(val, r)) +
            "[" +
            str(np.round(err, r)) +
            "]$")

def get_mean_std(df, min_flares=5, max_flares=30):
    """Calculate the mean and standard deviation of the waiting time
    distribution for a given dataframe with rot_phase being the rotational
    phase column.
    
    Parameters
    ----------
    df : pd.DataFrame
        The dataframe with the rot_phase column, and different stars with
        KIC IDs.
    min_flares : int, optional
        The minimum number of flares per star, by default 5
    max_flares : int, optional
        The maximum number of flares per star, by default 30

    Returns
    -------
    tuple
        The mean, standard deviation, number of stars, and number of flares
        in the subsample. The first two come with standard errors each.

    """
    # initialize the lists
    dat = []

    # set counter for total number of flares
    total_flares = 0
    total_stars = 0

    # loop over the stars
    for kic, g in df.sort_values(by="Date").groupby("KIC"):
        
        # between 5 and 30 flares per default
        if (g.shape[0] <= max_flares) & (g.shape[0] >= min_flares):

            # sort rotational phases, drop nans, calculate the waiting times
            # drop the first value, which is always nan
            agg = g.rot_phase.sort_values().dropna().diff().dropna()

            # add the last value, which is the difference between the last
            # and the first flare
            agg = pd.concat([agg, pd.Series(1. - g.rot_phase.max() - g.rot_phase.min())])
            
            # append the individual star's mean and std to the lists
            dat.append(agg.values)

            # add the number of flares to the counter
            total_flares += g.shape[0]
            total_stars += 1
    
    # flatten dat
    dat = np.concatenate(dat)

    return (np.nanmean(dat), np.nanstd(dat), total_stars, total_flares)



if __name__ == "__main__":

    # ----------------------------------------------------------------------
    # READ THE DATA

    # read in fits file
    hdu = fits.open('data/okamoto2021.fit')

    recar = hdu[1].data
    # convert recarray to dataframe
    df = pd.DataFrame(recar)
    for col in df.columns:
        # convert bin-endian to little-endian
        df[col] = df[col].values.byteswap().newbyteorder()

    # ----------------------------------------------------------------------
    # CALCULATE THE ROTATIONAL PHASE

    # calculate the rotational phase of the flares
    df["rot_phase"] = df.Date % df.Prot / df.Prot


    # ----------------------------------------------------------------------
    # CALCULATE THE MEAN AND STD OF THE WAITING TIME DISTRIBUTION

    # calculate the mean and std for various subsamples
    res = {}

    # rotate faster than 10 days, well-known rotation period, 
    fast = df[ (df.Prot<10.)  & (df.e_Prot/df.Prot<0.05)]
    min_rot = fast.Prot.min()
    max_rot = fast.Prot.max()
    res["all_fast"] = [5, 30, min_rot, max_rot, 0.05, *get_mean_std(fast)]

    # rotate between 5 and 10 days
    fast = df[ (df.Prot<10.)  & (df.e_Prot/df.Prot<0.05) & (df.Prot>=5)]
    min_rot = fast.Prot.min()
    max_rot = fast.Prot.max()
    res["5_10_fast"] = [5, 30, min_rot, max_rot, 0.05, *get_mean_std(fast)]

    # rotate faster than 5 days
    fast = df[ (df.Prot<5.)  & (df.e_Prot/df.Prot<0.05)]
    min_rot = fast.Prot.min()
    max_rot = fast.Prot.max()
    res["l5_fast"] = [5, 30, min_rot, max_rot, 0.05, *get_mean_std(fast)]

    # rotate slower than 10 days
    fast = df[ (df.Prot>=10)  & (df.e_Prot/df.Prot<0.05)]
    min_rot = fast.Prot.min()
    max_rot = fast.Prot.max()
    res["geq10_slow"] = [5, 30, min_rot, max_rot, 0.05, *get_mean_std(fast)]

    # ----------------------------------------------------------------------
    # WRITE THE TABLE TO FILE

    # rename the columns
    resdf = pd.DataFrame(res).T.rename(columns={0:"min_flares", 1:"max_flares", 
                                        2:"min_rot", 3:"max_rot", 
                                        4:"max_rot_err", 5:"mean", 
                                        6:"std", 7:"n_stars", 8:"n_flares"})


    # write to csv
    resdf.to_csv("results/okamoto2021_table.csv", index_label="sample_ID")


