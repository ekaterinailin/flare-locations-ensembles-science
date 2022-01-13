""" 
Script to calculate the relations used to decompose
ED into amplitude and FWHM using emprical relationship
between ED and amplitude from TESS UCD data (Pineda et al.
in prep.) and the inversion of the Davenport (2014) model,
as defined in his formulae (1) and (4).

Ekaterina Ilin 
MIT License (2022)
"""

import numpy as np
import pandas as pd
from scipy import stats


import json
from datetime import date

import matplotlib.pyplot as plt

# Factors extracted from Davenport 2014 formulae (1) and (4):
X = 0.6890 / 1.600 + 0.3030 / 0.2783
F, G, H, I = 1.941, -0.175 ,-2.246,-1.125

def ed_a_from_fwhm_with_davenport(fwhm):
    """Integrate and sum up formulas (1) and (4)
    in Davenport (2014) to obtain ED/amplitude.
    
    Parameters:
    -----------
    fwhm : float or array
        t_1/2 in Davenport (2014)
    
    Return:
    -------
    float or array - ED/amplitude
    """
    return 1 / fwhm**4 * (X * fwhm**5 + fwhm**4 + F / 2 * fwhm**3 + G / 3 * fwhm**2 + H / 4 * fwhm + I / 5)


if __name__ == "__main__":

   
    # get timestamp
    today = date.today().strftime("%Y_%m_%d")
    
    print("Calculating the decomposition of ED in a and FWHM:")
    print("-"*20)
    
    # --------------------------------------------------------------
    # --------------------------------------------------------------
    # GET ED-AMPLITUDE RELATIONSHIP

    # use TESS UCD flare table from Pineda et al. in prep.
    df = pd.read_csv("data/2021_12_08_flares.csv")
    
    # use real flares only
    df = df[df.real=="1"]
    
    #fit log-log linear relation to ED and a
    slope, intercept, r_value, p_value, std_err = stats.linregress(np.log10(df.ampl_rec.values),
                                                               np.log10(df.ed_rec.values))
    
    # save result
    with open("results/a_from_ed.json", "w") as file:
        dic = { "slope" : slope, "intercept" : intercept }
        json.dump(dic, file)
        print("ED-amplitude loglog-linear relation:\nslope: ", slope, "\nintercept: ", intercept)
        print("-"*20)
        
        
    # DIAGNOSTIC ------------------------------------------------
    # make and save plot of data:    
    plt.figure(figsize=(7, 5.5))
    
    # plot data
    plt.scatter(df.ampl_rec, df.ed_rec, marker="x",s=10, c="k",label="TESS UCD flares")
    
    # plot best-fit relationship
    x = np.linspace(-3,2,50)
    y = x * slope + intercept
    plt.plot(10**x,10**y,c="r",label=fr"$\log_{{10}}ED(a)={slope:.2f}\cdot \log_{{10}}a + {intercept:.2f}$")
    
    # layout
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("rel. amplitude")
    plt.ylabel("ED [s]");
    plt.legend()
    plt.savefig(f"plots/{today}_ED_over_a_in_TESS_UCD_flares.png", dpi=300)
    # -------------------------------------------------------------
    
    # --------------------------------------------------------------
    # --------------------------------------------------------------
    
    
    
    # --------------------------------------------------------------
    # --------------------------------------------------------------
    # FWHM-ED/AMPLITUDE RELATIONSHIP
    
    
    # fit a loglog-linear relationship to the polynomial ED/a(FWHM) in Davenport(2014):
    x = np.logspace(2,5,100)
    slope, intercept, r_value, p_value, std_err = stats.linregress(np.log10(x),
                                                                   np.log10(ed_a_from_fwhm_with_davenport(x)))
    # save results:
    with open("results/fwhm_from_ed_a.json", "w") as file:
        dic = { "slope" : slope, "intercept" : intercept }
        json.dump(dic, file)
        print("ED/amplitude-FWHM loglog-linear relation:\nslope: ", slope, "\nintercept: ", intercept)
        print("-"*20)
    
    
    # --------------------------------------------------------------
    # --------------------------------------------------------------
    
    
    

    
