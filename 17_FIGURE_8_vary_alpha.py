""" 
Python 3.8 -- UTF-8

Ekaterina Ilin 
MIT License (2022)

This script compares simulation runs with the only varying
parameter being the FFD slope alpha.

PRODUCES FIGURE 8 IN THE PAPER.

"""

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
plt.style.use('plots/paper.mplstyle')

if __name__ == "__main__":

    # select test runs to plot
    tstamps = [("2022_03_24_15_52_2022_03_24_15_18", 
                fr"$\alpha$ = 1.5-2.5, bihem., 1 spot, lat = 5 deg", 
                "#009E73"),
               ("2022_03_31_19_36_2022_03_31_18_50",
                fr"$\alpha$ = 2.5, bihem., 1 spot, lat = 5 deg", 
                "#56B4E9"),
               ("2022_03_24_16_18_2022_03_24_16_02", 
                fr"$\alpha$ = 2.0, bihem., 1 spot, lat = 5 deg", 
                "#230072B2"),
               ("2022_03_31_19_57_2022_03_31_19_41",
                fr"$\alpha$ = 1.5, bihem., 1 spot, lat = 5 deg", 
                "#CC79A7"),]

    # setup plots
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(6,8.5))

    # loop throught tstamps
    for tstamp, label, c in tstamps:

        # read in data
        df = pd.read_csv(f"results/{tstamp}_flares_train_merged.csv")

        # weed out bad data
        _ = df[(df.midlat2 > 0.) &
               (df.midlat2 < 90.) &
               (~df["diff_tstart_std_stepsize1"].isnull())]

        # make label
        alpha = label.split("alpha$ = ")[1].split(", bi")[0]
        if alpha=="1.5-2.5":
            alpha = 0.25
            c = "b"
        else:
            alpha= (float(alpha) / 2.5)**2
            
        l = label.split(", ")[0]
        
        # get means and stds
        means = _["diff_tstart_mean_stepsize1"] / 2. / np.pi
        stds = _["diff_tstart_std_stepsize1"] / 2. / np.pi

        # means histogram
        bins = np.linspace(0.06, 0.11, 14)
        binmids = (bins[1:] + bins[:-1]) / 2.
        histmeans, bins = np.histogram(means, bins=bins)

        ax[0].plot(binmids, histmeans, c="r", alpha=alpha, label=l)
        ax[0].axvline(np.mean(means),c="k", linestyle="dashed", alpha=alpha)
        ax[0].axvspan(np.mean(means) - np.std(means),
                       np.mean(means) + np.std(means),
                       facecolor="grey", alpha=alpha/2)    
        ax[0].set_xlim(binmids[0],binmids[-1])

        # stds histogram
        bins = np.linspace(0.03, 0.17, 14)
        binmids = (bins[1:] + bins[:-1]) / 2.
        histstds, bins = np.histogram(stds, bins=bins)

        ax[1].plot(binmids, histstds, c="r", alpha=alpha, label=l)
        ax[1].axvline(np.mean(stds),c="k", linestyle="dashed", alpha=alpha)
        ax[1].axvspan(np.mean(stds) - np.std(stds),
                       np.mean(stds) + np.std(stds),
                       facecolor="grey", alpha=alpha/2)
        ax[1].set_xlim(binmids[0],binmids[-1])

    # layout
    for a in ax:
        a.set_ylabel("number of ensembles", fontsize=14)
        a.legend(loc=1,fontsize=14, frameon=False)
        a.set_ylim(0,)

    ax[0].set_title(rf"1 spot, bi-hem.",fontsize=13)
    ax[0].set_xlabel("mean waiting time [rotation period]", fontsize=14)
    ax[1].set_xlabel("std waiting time [rotation period]", fontsize=14)
    plt.tight_layout()

    # save to file
    path = "plots/1spot_var_alpha.png"
    print("Saving plot to file: ", path)
    plt.savefig(path, dpi=300)