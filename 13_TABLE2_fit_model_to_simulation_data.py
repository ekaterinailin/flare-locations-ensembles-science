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

from scipy.odr import Model, RealData, ODR

import matplotlib.pyplot as plt
plt.style.use('plots/paper.mplstyle')

def latfit(b0,x):
    mu, sig = x
    a, b, c, d, e = b0
    return  a *  mu**2 + b * mu + c * sig**2  + d * sig + e 


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
    
    # loop through group frames of same hemisphere, number of spots and color
    for l, mono in res.groupby(["hem","nspots","color"]):
        
        # get label
        hem, nspots, color = l
        
        # make label
        tt = f"{nspots} spots, {hem}"
        
        dicspots = {"1-3":2, "1":1, "3-5":4}
        dicthem = {"bi-hem.":2., "mono-hem.":1.}
        print(hem)
        
        # setup result row
        fitres[tt]={}
        
        # init model
        f = Model(latfit)
        
        x1, x2, y = [], [], []
        
        # read in simulated data
        for _, d in mono.iterrows():
            
            
            df = pd.read_csv(f"results/{nstamp}_{d.tstamp[17:]}_flares_train_merged.csv")

            # select only data with mid latitude above 1 and below 89 deg, that also
            # have std measured
            _ = df[(df.midlat2 > 0.) &
                   (df.midlat2 < 90.) &
                   (~df["diff_tstart_std_stepsize1"].isnull())]

            # sort by mid latitude
            _ = _.sort_values(by="midlat2",ascending=True)
            y_ = _.midlat2.values
            
            # normalize to rotation period as unit
            x1_ = _["diff_tstart_mean_stepsize1"] / 2 / np.pi
            x2_ = _["diff_tstart_std_stepsize1"] / 2. / np.pi
            
            x1 = np.concatenate((x1, x1_.values))
            x2 = np.concatenate((x2, x2_.values))
            y = np.concatenate((y, y_))
        
        
        # 2D x-data
        x = np.array([x1, x2])
        
        # x-errors guessed
        sx = np.array([x1 / 10. / dicspots[nspots],
                       2.5 * x2 / np.sqrt(dicspots[nspots] * dicthem[hem])])
        
        # y-error same as in binning in script 12_
        sy = np.full_like(y, 2.5)
        
        # setup data for ODR fit
        mydata = RealData(x, y, sx=sx, sy=sy)

        # setup ODR fit
        myodr = ODR(mydata, f, 
                    beta0=[-5988. ,  5000.,
                           -4000.,    -4000.,
                           30.],
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
        fitres[tt]=dict(zip(["color",
                             "a","b","c","d","e",
                             "ar","br","cr","dr","er"],
                            np.concatenate(([mono.color.iloc[0]],
                                             myoutput.beta,
                                             myoutput.sd_beta))))
        
        # covariance matric out file
        stri = tt.replace(" ","_").replace("-","_").replace(",","").replace(".","")
        myoutput.cov_beta.tofile(f"results/{stri}_covmat.txt", sep=',')
        


    # save fitting data
    fitresd = pd.DataFrame(fitres)
    print(fitresd.columns, fitresd.index)
    fitresd.to_csv(f"results/fit_parameters.csv")

    
