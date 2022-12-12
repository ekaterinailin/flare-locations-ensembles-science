""" 
Python 3.8 -- UTF-8

Ekaterina Ilin 
MIT License (2022)

This script fits polynomials to the mean/std vs. latitude data
and computes uncertainties for all fits.

PRODUCES THE CSV FILE FOR TABLE 2 IN THE PAPER.

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

def latfit(b0,x):
    mu, sig = x
    a,b,c,d,e = b0
    return  a *  mu**2 + b * mu + c * sig + d +  e * sig*mu 

def latfit_err(b0err, x):
    mu, sig = x
    ar,br,cr,dr,er= b0err 
    return np.sqrt( + (mu**2 * ar)**2 + (br * mu)**2 + (cr * sig)**2 + dr**2 + (sig* mu * er)**2)

if __name__ == "__main__":

    
    # ----------------------------------------------------------------------------
    # FIT POLYNOMIALS
    
    print("Print unbinned data with polynomials:\n")
    nstamp = "2022_06_30_10_00"
    
    # read in all runs
    res = pd.read_csv("results/2022_05_all_runs.csv")
    
    # read in the mean std results
    ms = pd.read_csv(f"results/{nstamp}_all_mean_stds.csv")
    
    # init results
    fitres = {}
    
    # loop through setups
    for color in ms.c.unique():
        
        # pick setup
        mono = ms[ms.c == color]
        
        # make label
        tt = f"{mono.nspots.iloc[0]} spots, {mono.hem.iloc[0]}"
        
        # setup result row
        fitres[tt]={}
        
        # init model
        f = Model(latfit)
        
        # 2D x-data
        x = np.array([mono.mean_of_wtd_means.values, 
                      mono.mean_of_wtd_stds.values])
        
        # y-data
        y = mono.latitude.values
        
        # x-error
        sx = np.array([mono.std_of_wtd_means.values,
                       mono.std__of_wtd_stds.values])
        
        # y-error same as in binning in script 12_
        sy = np.full_like(y, 3.)
        
        # setup data for ODR fit
        mydata = RealData(x, y, sx=sx, sy=sy)

        # setup ODR fit
        myodr = ODR(mydata, f, 
                    beta0=[-1788.8766187 ,  1627.4705935 ,
                           1562.95810747,    -1181.56885256,
                           82.],
                    maxit=15000)
        
        # run ODR fit
        myoutput = myodr.run()
        
        # print output
        print("----------------------------------------")
        print(tt)
        print(myoutput.pprint())
        
        
        # some diagnosticts for each fit
        mono["minflares"]=mono.nflares.apply(lambda x: float(x.split("-")[0]))
        mono["maxflares"]=mono.nflares.apply(lambda x: float(x.split("-")[-1]))
        mono = mono.sort_values("minflares",ascending=True)
        
        # add results line
        fitres[tt]=dict(zip(["color","a","b","c","d",
                             "e","ar","br","cr","dr","er"],
                            np.concatenate(([mono.c.iloc[0]],
                                             myoutput.beta,myoutput.sd_beta))))

        # ----------------------------------------------------------------------------
        # PLOT FITTING RESULTS
        
        # setup axes
        axes = [0,0,0,1,1,1,2,2]
        fig, AX = plt.subplots(nrows=1, ncols=3, figsize=(14,5), sharey=True)
        
        # loops through results
        for ax, (label, g) in list(zip(axes, mono.groupby(["minflares","maxflares"]))):
            
            # x-data
            x = np.array([g.mean_of_wtd_means.values,
                          g.mean_of_wtd_stds.values])
            # y-data
            y = g.latitude.values
            
            # plot the fit
            AX[ax].errorbar(y,latfit(myoutput.beta,x),xerr=2.5,yerr=latfit_err(myoutput.sd_beta,x),
                         label=label,fmt="o",markersize=7, alpha=1,capsize=4)
            
            # add 1-1 line
            AX[ax].plot([0,90],[0,90],c="k")
            
            # layout
            AX[ax].set_xlim(0,90)
            AX[ax].set_ylim(-90,180)
            AX[ax].set_xlabel("true latitude [deg]")
            AX[ax].legend()
            
        # layout    
        AX[0].set_ylabel("inferred latitude [deg]")
        AX[1].set_title(f"{mono.nspots.iloc[0]} spots, {mono.hem.iloc[0]}",fontsize=20)
        plt.tight_layout()
        
        # save to file
        ps2 = f"plots/{mono.nspots.iloc[0]}_spots_{mono.hem.iloc[0]}_fit_5params"
        print(f"Plotted to {ps2}.")
        plt.savefig(ps2.replace("-","_").replace(".",""),dpi=300)
        
        
    # save fitting data
    fitresd = pd.DataFrame(fitres)
    print(fitresd.columns, fitresd.index)
    fitresd.to_csv(f"results/fit_parameters.csv")

    
