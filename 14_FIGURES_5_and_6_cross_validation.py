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

import matplotlib.pyplot as plt
plt.style.use('plots/paper.mplstyle')


def latfit(b0,x):
    mu, sig = x
    a,b,c,d,e = b0
    return  a * mu**2 + b * mu  + c * sig**2  + d * sig +  e


def latfit_err(b0err, x):
    mu, sig = x
    ar,br,cr,dr,er= b0err 
    return np.sqrt((mu**2 * ar)**2 + (mu * br)**2  + (sig * dr)**2 + er**2 + (sig**2 * cr)**2)
   

if __name__ == "__main__":
    
    
    # --------------------------------------------------------------
    # CROSS-VALIDATE
    
    # read in all runs
    res = pd.read_csv("results/2022_05_all_runs.csv")
    
    # read in fitting results from script 13_
    fitresd = pd.read_csv(f"results/fit_parameters.csv").set_index("Unnamed: 0")
    
    
    for case, d in fitresd.T.iterrows():


        # pick the right setup
        print(case)
        stri = case.replace(" ","_").replace("-","_").replace(",","").replace(".","")
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
            x = df[["diff_tstart_mean_stepsize1", "diff_tstart_std_stepsize1"]] / 2. / np.pi

            # use parametrization to infer latitudes
            df["inferred_lat"] = latfit(params, x.values.T)

            # caclucate errors using covariance matrix
            covmat = np.genfromtxt(f"results/{stri}_covmat.txt", delimiter=",").reshape((5,5))
            
            err = []
            for ind, val in x.iterrows():
                mu, sig = val.values
                vec = np.array([mu**2, mu, sig**2, sig, 1.])
                err.append(np.sqrt(np.matmul(vec.T, np.matmul(covmat, vec))))
   
            # remove all failed inferences optionally
#             df.loc[df["inferred_lat"] > 90.,"inferred_lat"] = np.nan
#             df.loc[df["inferred_lat"] < 0.,"inferred_lat"] = np.nan
#             df.loc[df["inferred_lat_err"] > 90.,"inferred_lat"] = np.nan

            # concatenate all datasets
            inflats = np.concatenate((inflats, df.inferred_lat.values))
            inflatserr = np.concatenate((inflatserr, err))
            truelats = np.concatenate((truelats, df.midlat2.values))
            meanwtd = np.concatenate((meanwtd, x["diff_tstart_mean_stepsize1"].values))
        
        fig, axes =  plt.subplots(nrows=4, ncols=1, figsize=(7, 17.5), sharex=True, sharey=True)
        # group results by error size and color code
        colors = ['#17becf', '#8c564b', '#e377c2', 'k']
        wtds = [.2, .15, .10, 0.05, 0.01]
        for wtdmax, wtdmin, c, ax in list(zip(wtds[:-1], wtds[1:], colors, axes)):
            
            # color code based on mean waiting time
            ins = (meanwtd > wtdmin) & (meanwtd < wtdmax) & (truelats > 5) & (truelats < 85)
            
            if truelats[ins].shape[0] > 0:
                ax.errorbar(x=truelats[ins],
                            y=inflats[ins] - truelats[ins],
                            yerr = inflatserr[ins],
                            linewidth=0.5, color="k",
                            alpha=0.5, fmt=".", markersize=1,
                            )
                ax.scatter(x=truelats[ins],
                           y=inflats[ins] - truelats[ins],
                           zorder=10,
                           s=34, c=c,
                           label=fr"{wtdmin} < mean waiting time < {wtdmax} rot. per.")    
            
            ax.legend(frameon=False)
    
        # layout
        axes[-1].set_xlabel("true latitude [deg]")
        for ax in axes:
            
            # add 0-line
            ax.plot([0,90], [0,0], c="grey")
            ax.set_ylabel("inferred lat. - true lat. [deg]")
            ax.set_ylim(-90, 90)
            ax.set_xlim(5, 85)
            
        plt.subplots_adjust(wspace=None, hspace=None)
        plt.tight_layout()
       
        # save to file
        plt.savefig(f"plots/residuals_{stri}.png")