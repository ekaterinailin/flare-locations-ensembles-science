""" 
Python 3.8 -- UTF-8

This script takes all simulations and calculates the mean
and std values of all ensembles. Then

Ekaterina Ilin 
MIT License (2022)
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
    
    print(fitresd.head())
    
    for case, color in fitresd.T["color"][-2:-1].iteritems():

        # pick the right setup
        sets = res[res.color == color]
        colors = ['#17becf', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
        print(case)
        # for each case, create a table
        tab = {}

        for c, col in list(zip(colors,fitresd)):
            
            column = fitresd[col]
            params = column[list("abcde")].values.astype(float)
            paramerrs = column[["ar","br","cr","dr","er"]].values.astype(float)
            inflats, truelats, inflatserr = [],[],[]
            i=0

            # for each case, each interpretation gets a subtable
            tab[col] = {}

            for s, row in sets.iterrows():

                # for each interpretation each data set of the original will be added
                string = f"results/{row.tstamp[17:]}_flares_validate_merged.csv"
                df = pd.read_csv(string)#.iloc[::5]
                x = df[["diff_tstart_mean_stepsize1","diff_tstart_std_stepsize1"]]/2./np.pi
                df["inferred_lat"] = latfit(params,x.values.T)
                df["inferred_lat_err"] = latfit_err(paramerrs,x.values.T)
                df.loc[df["inferred_lat"]>90.,"inferred_lat"] = np.nan
                df.loc[df["inferred_lat"]<0.,"inferred_lat"] = np.nan
                df.loc[df["inferred_lat_err"]>90.,"inferred_lat"]=np.nan

                # for each interpretation each data set of the original will be added

                inflats = np.concatenate((inflats, df.inferred_lat.values))
                inflatserr = np.concatenate((inflatserr, df.inferred_lat_err.values))
                truelats = np.concatenate((truelats,df.midlat2.values))

            tab[col]["truelat"] = truelats
            tab[col]["inflat"] = inflats
            tab[col]["inflat_err"] = inflatserr
            
        reform = {(outerKey, innerKey): values for outerKey, innerDict in 
                  tab.items() for innerKey, values in innerDict.items()}

        ff = pd.DataFrame(reform)

        fff = ff.T.reset_index().dropna(subset=[1], axis=1)#.drop([3,4,5,7,8,10,11,13,14,6,9,12])
        fff = fff.replace("1 spots, bi-hem.","1 spot")
        print(fff.head(20))
        
        # plot validation
        colors = ['#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
        plt.figure(figsize=(7.5,6.5))
        ffff = fff.drop(["level_0","level_1"],axis=1)
        truelat = ffff.iloc[9]#[::-2]
        inflat = ffff.iloc[10]#[::-2]
        inflaterr = ffff.iloc[11]#[::-2]

        plt.errorbar(x=truelat, y=inflat - truelat, yerr=inflaterr, fmt="o",
                     markersize=0, linewidth=0.5, capsize=2, c="grey", zorder=-10)
        
        for err,c in list(zip([60, 30, 20, 10],colors)):
            ins = inflaterr < err
            if truelat[ins].shape[0]>0:
                plt.scatter(x=truelat[ins], y=inflat[ins] - truelat[ins],
                            s=34, c=c, label=fr"error < ${err}^\circ$")    
        
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