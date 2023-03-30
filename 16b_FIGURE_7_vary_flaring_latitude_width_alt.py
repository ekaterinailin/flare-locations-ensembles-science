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
        dtheta = int(label.split("lat = ")[1].split(" deg")[0])
        alpha = dtheta / 40.
        l = label.split("spots, ")[1].split(", mono")[0]
        l = l.replace("lat",r"$\Delta\theta$").replace(" deg",r"$^\circ$")

        # get means and stds
        means = _["diff_tstart_mean_stepsize1"] / 2. / np.pi
        stds = _["diff_tstart_std_stepsize1"] / 2. / np.pi


        # make a violin plot for means
        violinparts = ax[0].violinplot(means, positions=[dtheta], #quantiles=[.05,.95],
                         showmedians=True, widths=4)
        
        for pc in violinparts['bodies']:
            
            pc.set_facecolor('#009E73')
            pc.set_edgecolor('grey')


        for partname in ('cbars','cmins','cmaxes','cmedians'):
            violinparts[partname].set_color('k')
           
        ax[0].set_xlabel(r"$\Delta\theta$ [deg]")
        ax[0].set_ylabel(r"$\mu$  [rot. per.]")


        # make a violin plot for stds
        violinparts = ax[1].violinplot(stds, positions=[dtheta], #quantiles=[.05,.95],
                            showmedians=True, widths=4)
        

        for pc in violinparts['bodies']:
            pc.set_facecolor('#009E73')
            pc.set_edgecolor('grey')

        for partname in ('cbars','cmins','cmaxes','cmedians'):
            violinparts[partname].set_color('k')


        ax[1].set_xlabel(r"$\Delta\theta$ [deg]")
        ax[1].set_ylabel(r"$\sigma$ [rot. per.]")
    

    ax[0].set_title(rf"1-3 spots, mono-hem.",fontsize=15)
    plt.tight_layout()

    # save to file
    path = "plots/123spots_var_delta_theta_alt.png"
    print("Saving plot to file: ", path)
    plt.savefig(path, dpi=300)