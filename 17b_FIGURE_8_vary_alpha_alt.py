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
    tstamps = [
        # ("2022_03_24_15_52_2022_03_24_15_18", 
        #         fr"$\alpha$ = 1.5-2.5, bihem., 1 spot, lat = 5 deg", 
        #         "#009E73"),
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

        # x-value
        alpha = label.split("alpha$ = ")[1].split(", bi")[0]

        l = label.split(", ")[0]
        
        # get means and stds
        means = _["diff_tstart_mean_stepsize1"] / 2. / np.pi
        stds = _["diff_tstart_std_stepsize1"] / 2. / np.pi

               # make a violin plot for means
        violinparts = ax[0].violinplot(means, positions=[float(alpha)], #quantiles=[.05,.95],
                         showmedians=True, widths=.25)
        
        for pc in violinparts['bodies']:
            
            pc.set_facecolor('#009E73')
            pc.set_edgecolor('grey')


        for partname in ('cbars','cmins','cmaxes','cmedians'):
            violinparts[partname].set_color('k')
           
        ax[0].set_xlabel(r"$\alpha$")
        ax[0].set_ylabel(r"$\mu$  [rot. per.]")


        # make a violin plot for stds
        violinparts = ax[1].violinplot(stds, positions=[float(alpha)], #quantiles=[.05,.95],
                            showmedians=True, widths=.25)
        

        for pc in violinparts['bodies']:
            pc.set_facecolor('#009E73')
            pc.set_edgecolor('grey')

        for partname in ('cbars','cmins','cmaxes','cmedians'):
            violinparts[partname].set_color('k')


        ax[1].set_xlabel(r"$\alpha$")
        ax[1].set_ylabel(r"$\sigma$ [rot. per.]")
    

    # on both x-axes, replace with 1.5, 2.0, and 2.5 ticks and labels
    for a in ax:
        a.set_xticks([1.5, 2.0, 2.5])
        a.set_xticklabels([r"1.5", r"2.0", r"2.5"])


    ax[0].set_title(rf"1 spot, bi-hem.",fontsize=13)
    plt.tight_layout()

    # save to file
    path = "plots/1spot_var_alpha_alt.png"
    print("Saving plot to file: ", path)
    plt.savefig(path, dpi=300)