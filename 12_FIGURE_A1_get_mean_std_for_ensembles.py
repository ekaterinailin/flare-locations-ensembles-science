""" 
Python 3.8 -- UTF-8

This script takes all simulations and calculates the mean
and std values of all ensembles.

PRODUCES FIGURE A1 IN THE APPENDIX OF THE PAPER.

Ekaterina Ilin 
MIT License (2022)
"""

import numpy as np
import pandas as pd


from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
plt.style.use('plots/paper.mplstyle')


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
    
    # loop through group frames of same hemisphere, number of spots and color
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
            _ = df[(df.midlat2 > 0.) &
                   (df.midlat2 < 90.) &
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
        legend_handles = []
        legend_labels = []
        
        for N in Ns:
            print(label)
            
            # make label
            if "1," in label:
                labe = fr"$\theta={N:2d}^\circ$, 1 spot"
            else:
                _ = label.split("hem")[0] + "hem."
                _ = _[:3] + " spots" + _[3:]
                labe = fr"$\theta={N:2d}^\circ$, {_}"
                
            print(labe)
            
            # latitude 80 deg line
            if N == 80:
                
                # in current subplot, and summary subplot
                for a, l in list(zip([ax, axs[-1]], [labe, None])):
                    
                    # in current subplot    
                    a.errorbar(latlinesmean[N],latlinesstd[N],
                                xerr=std_latlinesmean[N], yerr=std_latlinesstd[N],
                                linestyle="dashed", alpha=1,
                                linewidth=2, c=color,zorder=40,)

                # in all other subplots
                for a in axs[:-1]:
                    a.plot(latlinesmean[N],latlinesstd[N],linestyle="dashed", alpha=0.5,
                    linewidth=2, c="grey")
                    
                legend_handles.append(Line2D([0], [0], color=color, lw=4, linestyle="dashed"))
                legend_labels.append(labe)

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
                    
                legend_handles.append(Line2D([0], [0], color=color, lw=4, linestyle="dotted"))
                legend_labels.append(labe)
            
            # 5 deg latitude line
            elif N == 10:
                
                # in current subplot, and summary subplot
                for a, l in list(zip([ax, axs[-1]], [labe, None])):
                
                    a.errorbar(latlinesmean[N],latlinesstd[N],
                                xerr=std_latlinesmean[N], yerr=std_latlinesstd[N],
                                linestyle="solid", alpha=1,
                                linewidth=2, c=color,zorder=40)
                
                # in all subplots
                for a in axs[:-1]:
                    a.plot(latlinesmean[N],latlinesstd[N],
                           linestyle="solid", alpha=.5,
                           linewidth=1, c="grey")
                    
                legend_handles.append(Line2D([0], [0], color=color, lw=4, linestyle="solid"))
                legend_labels.append(labe)
    
        ax.set_xlim(0.05, .2)
        ax.set_ylim(0.025, 0.2)

        # add legend
        ax.legend(legend_handles, legend_labels, loc=4, frameon=False)

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
    
 