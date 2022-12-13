""" 
Python 3.8 -- UTF-8

Ekaterina Ilin 
MIT License (2022)

This script compares simulation runs with the only varying
parameter being the flaring latitude width.

PRODUCES FIGURE 7 IN THE PAPER.

"""

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
plt.style.use('plots/paper.mplstyle')

if __name__ == "__main__":

    # The setups to study delta theta
    tstamps = [("2022_03_26_07_30_2022_03_26_07_09", "1-3 spots, lat = 5 deg, monohem.", "#009E73"),
               ("2022_03_28_18_33_2022_03_28_14_45","1-3 spots, lat = 10 deg, monohem.", "#56B4E9"),
               ("2022_03_28_18_57_2022_03_28_18_36","1-3 spots, lat = 20 deg, monohem.", "#230072B2"),
                ("2022_03_28_19_20_2022_03_28_19_02","1-3 spots, lat = 40 deg, monohem.", "#CC79A7")
              ]

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
        alpha = int(label.split("lat = ")[1].split(" deg")[0]) / 40.
        l = label.split("spots, ")[1].split(", mono")[0]
        l = l.replace("lat",r"$\Delta\theta$").replace(" deg",r"$^\circ$")

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
        bins = np.linspace(0.05, 0.13, 14)
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

    ax[0].set_title(rf"1-3 spots, mono-hem.",fontsize=13)
    ax[0].set_xlabel("mean waiting time [rotation period]", fontsize=14)
    ax[1].set_xlabel("std waiting time [rotation period]", fontsize=14)
    plt.tight_layout()

    # save to file
    path = "plots/123spots_var_delta_theta.png"
    print("Saving plot to file: ", path)
    plt.savefig(path, dpi=300)