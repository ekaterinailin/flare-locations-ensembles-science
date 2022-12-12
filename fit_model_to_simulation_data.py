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

    # Read the list of all runs
    res = pd.read_csv("results/2022_05_all_runs.csv")
    nstamp = "2022_06_30_10_00"
    
    print("Get all mean and std of waiting times:\n")
    
    # init the results table
    with open(f"results/{nstamp}_all_mean_stds.csv","w") as f: 
        string = (f"tstamp,nspots,hem,nflares,c,latitude,mean_of_wtd_means,"
                  "mean_of_wtd_stds,std_of_wtd_means,std__of_wtd_stds,nensembles\n")
        f.write(string)

    # init the plot
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(19,12),sharex=True, sharey=True)
    
    # What latitudes
    Ns = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]
    
    # flatten the nested list of axes
    axs = [ap for a in axs for ap in a]
    
    # init dict
    nonlat = {}
    
    # loop through group frames of same hemisphere, numver of spots and color
    for (l, g), ax in  list(zip(res.groupby(["hem","nspots","color"]), axs[:-1])):
        
        # get label
        hem, nspots, color = l
        
        # init dict
        latlinesmean, latlinesstd = {}, {}        
        std_latlinesmean, std_latlinesstd = {}, {}
        
        # init linestyles
        linestyle = ["solid", "dashed", "dotted", "dashdot", ':', 
                     "solid", "dashed", "dotted", "dashdot", ':']
        
        # make a list of results for each latitude
        for N in Ns:
            latlinesmean[N] = []
            latlinesstd[N] =  []
            std_latlinesmean[N] = []
            std_latlinesstd[N] =  []

        # loop through simulated data
        for i, (tstamp, nspots, hem, nflares, c) in g.iterrows():
            
            # make label
            label = f"{nspots}, {hem}, {nflares}"
            
            # read in simulated data
            df = pd.read_csv(f"results/{nstamp}_{tstamp[17:]}_flares_train_merged.csv")

            # select only data with mid latitude above 1 and below 89 deg, that also
            # have std measured
            _ = df[(df.midlat2 > 1.) &
                   (df.midlat2 < 89.) &
                   (~df["diff_tstart_std_stepsize1"].isnull())]

            # sort by mid latitude
            _ = _.sort_values(by="midlat2",ascending=True)
            z = _.midlat2.values
            
            # normalize to rotation period as unit
            x = _["diff_tstart_mean_stepsize1"] / 2 / np.pi
            y = _["diff_tstart_std_stepsize1"] / 2. / np.pi

            # loop through latitudes
            for N in Ns:
                
                # make sure latitudes are within the width
                idx = ((z>(N - 3)) & (z<(N + 3)))

                # add mean mean and std values in sets of ensembles
                latlinesmean[N].append(x[idx].mean())
                latlinesstd[N].append(y[idx].mean())
                
                # add std mean and std values in sets of ensembles
                std_latlinesmean[N].append(x[idx].std())
                std_latlinesstd[N].append(y[idx].std())
                
                # write out to file
                with open(f"results/{nstamp}_all_mean_stds.csv","a") as f:
                    string = (f"{nstamp}_{tstamp[17:]},{nspots},"
                              f"{hem},{nflares},{c},{N},"
                              f"{x[idx].mean()},{y[idx].mean()},"
                              f"{x[idx].std()},{y[idx].std()},{len(x[idx])}\n")
                    f.write(string)

        # ---------------------------------------------------------------------------
        # MAKE BIG PLOT
        for N in Ns:
            
            # make label
            if "1 spot" in label:
                labe = fr"$\theta={N:2d}^\circ$, 1 spot"
            else:
                _ = label.split("hem")[0] + "hem."
                labe = fr"$\theta={N:2d}^\circ$, {_}"
            
            # latitude 85 deg line
            if N == 80:
                
                # in current subplot, and summary subplot
                for a, l in list(zip([ax, axs[-1]], [labe, None])):
                        
#                     # plot mean and std in both
#                     a.scatter(latlinesmean[N], latlinesstd[N],s=10,
#                            linestyle="dashed", alpha=1,
#                            linewidth=3, c=color, zorder=40, label=l)
                    
                    # in current subplot    
                    a.errorbar(latlinesmean[N],latlinesstd[N],
                                xerr=std_latlinesmean[N], yerr=std_latlinesstd[N],
                                linestyle="dashed", alpha=1,
                                linewidth=2, c=color,zorder=40,)

                # in all other subplots
                for a in axs[:-1]:
                    a.plot(latlinesmean[N],latlinesstd[N],linestyle="dashed", alpha=0.5,
                    linewidth=2, c="grey")

            # at mid latitude
            elif N==45:
               
                # current subplot
                ax.scatter(latlinesmean[N],latlinesstd[N],s=10,
                        alpha=1,linestyle="dotted",linewidth=3,
                        c=color,zorder=40,label=labe)
                
                ax.errorbar(latlinesmean[N],latlinesstd[N],
                            xerr=std_latlinesmean[N], yerr=std_latlinesstd[N],
                            alpha=1,linestyle="dotted",linewidth=2,
                            c=color,zorder=40,)
                
                # for all other subplots
                for a in axs[:-1]:
                    a.plot(latlinesmean[N], latlinesstd[N], 
                           linestyle="dotted", alpha=0.5,
                           linewidth=1, c="grey")
            
            # 5 deg latitude line
            elif N == 10:
                
                # in current subplot, and summary subplot
                for a, l in list(zip([ax, axs[-1]], [labe, None])):
                
#                     a.scatter(latlinesmean[N],latlinesstd[N],
#                            linestyle="solid", alpha=1, s=10,
#                            linewidth=3, c=color,zorder=40,
#                            label=l)
                
                    a.errorbar(latlinesmean[N],latlinesstd[N],
                                xerr=std_latlinesmean[N], yerr=std_latlinesstd[N],
                                linestyle="solid", alpha=1,
                                linewidth=2, c=color,zorder=40)
                
                # in all subplots
                for a in axs[:-1]:
                    a.plot(latlinesmean[N],latlinesstd[N],
                           linestyle="solid", alpha=.5,
                           linewidth=1, c="grey")
    
        ax.set_xlim(0.05, .2)
        ax.set_ylim(0.025, 0.2)


    # add axes labels
    for i in [0,3]: 
        axs[i].set_ylabel(r"std waiting time $\sigma$ [rotation period]", fontsize=14)

    for i in [3,4,5]:
        axs[i].set_xlabel(r"mean waiting time $\mu$ [rotation period]", fontsize=14)

    # add subplot numbering
    subplots = list("abcdef")
    for ax, subplot in list(zip(axs, subplots)):
        ax.text(0.03, .97, f"({subplot})",
                horizontalalignment='left',
                verticalalignment='top',
                transform=ax.transAxes,
                fontsize=15)

    plt.tight_layout()
    
    ps1 = f"plots/12345spots_10_45_85deg_monobihem.png"
    print(f"Plotted to {ps1}.\n")
    plt.savefig(ps1, dpi=300)
    
    # ----------------------------------------------------------------------------
    # FIT POLYNOMIALS
    
    print("Print unbinned data with polynomials:\n")
    # Fit unbinned data
    
    # read in the mean std results
    ms = pd.read_csv(f"results/{nstamp}_all_mean_stds.csv")
    
    # init results
    fitres = {}
    
    for color in ms.c.unique()[:]:
        mono= ms[ms.c == color]
        tt = f"{mono.nspots.iloc[0]} spots, {mono.hem.iloc[0]}"
        fitres[tt]={}
        f = Model(latfit)
        x = np.array([mono.mean_of_wtd_means.values, 
                      mono.mean_of_wtd_stds.values])
        y = mono.latitude.values
        sx = np.array([mono.std_of_wtd_means.values,
                       mono.std__of_wtd_stds.values])
        sy = np.full_like(y,2.5)
        mydata = RealData(x, y, sx=sx, sy=sy)

        myodr = ODR(mydata, f, 
                    beta0=[-1788.8766187 ,  1627.4705935 , 1562.95810747,    -1181.56885256,82.],
                    maxit=15000)
        fitres[tt]={}
        myoutput = myodr.run()
        print(myoutput.pprint())
        mono["minflares"]=mono.nflares.apply(lambda x: float(x.split("-")[0]))
        mono["maxflares"]=mono.nflares.apply(lambda x: float(x.split("-")[-1]))
        mono = mono.sort_values("minflares",ascending=True)
        fitres[tt]=dict(zip(["color","a","b","c","d","e","ar","br","cr","dr","er"],
                            np.concatenate(([mono.c.iloc[0]],myoutput.beta,myoutput.sd_beta))))

        axes = [0,0,0,1,1,1,2,2]
        fig, AX = plt.subplots(nrows=1, ncols=3, figsize=(14,5),sharey=True)
        for ax, (label, g) in list(zip(axes,mono.groupby(["minflares","maxflares"]))):
    #         print(label)
            x = np.array([g.mean_of_wtd_means.values,g.mean_of_wtd_stds.values])
            y = g.latitude.values
            AX[ax].errorbar(y,latfit(myoutput.beta,x),xerr=2.5,yerr=latfit_err(myoutput.sd_beta,x),
                         label=label,fmt="o",markersize=7, alpha=1,capsize=4)
            AX[ax].plot([0,90],[0,90],c="k")
            AX[ax].set_xlim(0,90)
            AX[ax].set_ylim(-90,180)
            AX[ax].set_xlabel("true latitude [deg]")
            AX[ax].legend();
        AX[0].set_ylabel("inferred latitude [deg]")
        AX[1].set_title(f"{mono.nspots.iloc[0]} spots, {mono.hem.iloc[0]}",fontsize=20)
        plt.tight_layout()
        
        ps2 = f"plots/{nstamp}_{mono.nspots.iloc[0]}_spots_{mono.hem.iloc[0]}_fit_5params"
        print(f"Plotted to {ps2}.")
        plt.savefig(ps2.replace("-","_").replace(".",""),dpi=300)
        
        
    # save fitting data

    fitresd = pd.DataFrame(fitres)
    fitresd.to_csv(f"results/{nstamp}_fit_parameters.csv")

    # cross-validate
    
    for case, color in fitresd.T.color[-2:-1].iteritems():

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
        #         print(s)
                string = f"results/{nstamp}_{row.tstamp[17:]}_flares_validate_merged.csv"
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
        reform = {(outerKey, innerKey): values for outerKey, innerDict in tab.items() for innerKey, values in innerDict.items()}

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

        plt.errorbar(x=truelat, y=inflat-truelat, yerr=inflaterr,fmt="o",
                     markersize=0,linewidth=0.5,capsize=2,c="grey",zorder=-10)
        for err,c in list(zip([60,30,20,10],colors)):
            ins = inflaterr < err
        #     print(err, inflaterr[ins])
            plt.scatter(x=truelat[ins], y=inflat[ins]-truelat[ins],s=34,c=c, label=fr"error < ${err}^\circ$")    
        plt.plot([0,90],[0,0],c="grey")
        plt.xlabel("true latitude [deg]")
        plt.ylabel("residual [deg]")
        plt.ylim(-90,90)
        plt.xlim(0,90)
        plt.legend(frameon=False)
        plt.savefig(f"plots/{nstamp}_residuals_1spot_grouped.png");