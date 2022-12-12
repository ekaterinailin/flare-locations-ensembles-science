""" 
Python 3.8 -- UTF-8

Ekaterina Ilin 
MIT License (2022)

This script uses the polynomial fits from script 13_ 
(Table 2 in the paper) and applies it to the validation
data set.

PRODUCES FIGURES 5 AND 6 IN THE PAPER.

"""

import numpy as np
import pandas as pd
from datetime import datetime
import sys
from scipy.odr import Model, RealData, ODR

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
plt.style.use('plots/paper.mplstyle')

from flares.__init__ import (SCRIPT_NAME_GET_AGGREGATE_PARAMETERS,
							 SCRIPT_NAME_MERGE_FILES,
							)

def latfit(b0, x):
    mu, sig = x
    a,b,c,d,e = b0
    return  a *  mu**2 + b * mu + c * sig + d +  e * sig*mu 

def latfit_err(b0err, x):
    mu, sig = x
    ar,br,cr,dr,er= b0err 
    return np.sqrt( + (mu**2 * ar)**2 + (br * mu)**2 + (cr * sig)**2 + dr**2 + (sig* mu * er)**2)

if __name__ == "__main__":
    
    
    # --------------------------------------------------------------
    # CROSS-VALIDATE
    
    # read in all runs
    res = pd.read_csv("results/2022_05_all_runs.csv")
    
    # read in fitting results from script 13_
    fitresd = pd.read_csv(f"results/fit_parameters.csv").set_index("Unnamed: 0")
    
    print(fitresd.T.head())
    
    for case, d in fitresd.T.iterrows():

        plt.figure(figsize=(7.5, 6.5))
        # pick the right setup
        print(case)
        color = d["color"]
        sets = res[res.color == color]
        
        # get fit parameters
        params = d[list("abcde")].values.astype(float)
        paramerrs = d[["ar","br","cr","dr","er"]].values.astype(float)
        
        
        inflats, truelats, inflatserr, meanwtd = [],[],[],[]
        
        # each setup has a bunch of runs with different flare rates, 
        # which we all want to incorporate
        for s, row in sets.iterrows():

            # get validation data set
            string = f"results/{row.tstamp[17:]}_flares_validate_merged.csv"
            df = pd.read_csv(string)
            
            # convert units from radian to rotation period
            x = df[["diff_tstart_mean_stepsize1", "diff_tstart_std_stepsize1"]] / 2. /np.pi

            # use parametrization to infer latitudes
            df["inferred_lat"] = latfit(params, x.values.T)
            df["inferred_lat_err"] = latfit_err(paramerrs, x.values.T)

            # remove all failed inferences optionally
#             df.loc[df["inferred_lat"] > 90.,"inferred_lat"] = np.nan
#             df.loc[df["inferred_lat"] < 0.,"inferred_lat"] = np.nan
#             df.loc[df["inferred_lat_err"] > 90.,"inferred_lat"] = np.nan

            # concatenate all datasets

            inflats = np.concatenate((inflats, df.inferred_lat.values))
            inflatserr = np.concatenate((inflatserr, df.inferred_lat_err.values))
            truelats = np.concatenate((truelats, df.midlat2.values))
            meanwtd = np.concatenate((meanwtd, x["diff_tstart_mean_stepsize1"].values))
        
        # group results by error size and color code
        colors = ['#17becf', '#8c564b', '#e377c2', 'k']
        for err, c in list(zip([.25, .15, .10, 0.05], colors)):
            
            ins = meanwtd < err
            if truelats[ins].shape[0] > 0:
                plt.scatter(x=truelats[ins], y=inflats[ins] - truelats[ins],
                            s=34, c=c, label=fr"mean waiting time < {err} rot. per.")    
        
        # add 1-1 line
        plt.plot([0,90], [0,0], c="grey")
        
        # layout
        plt.xlabel("true latitude [deg]")
        plt.ylabel("inferred latitude - true latitude [deg]")
        plt.ylim(-90, 90)
        plt.xlim(0, 90)
        plt.legend(frameon=False)
        
        # save to file
        stri = case.replace(" ","_").replace("-","_").replace(",","")
        plt.savefig(f"plots/residuals_{stri}.png")