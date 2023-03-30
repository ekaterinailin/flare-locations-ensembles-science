""" 
Python 3.8 -- UTF-8

Ekaterina Ilin 
MIT License (2022)

This script uses the polynomial fits from script 13_ 
(Table 2 in the paper) plots the results to show the 
parameter space covered.

PRODUCES FIGURE 4 IN THE PAPER.

"""

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
plt.style.use('plots/paper.mplstyle')

from matplotlib.lines import Line2D

def sig(theta, mu, b0):
    """Inverts the parametrization in Eq. 2"""
    a, b, c, d, e = b0
    C = a * mu**2 + b * mu + e - theta
    A = c
    B = d
    return (-B - np.sqrt(B**2 - 4 * A * C)) / 2. / A

if __name__ == "__main__":

    # get fit parameters tables
    fitresd = pd.read_csv(f"results/fit_parameters.csv").set_index("Unnamed: 0")

    # init figure
    plt.figure(figsize=(7,5.5))

    # init labels
    handles, labels = [], []

    # define xlims
    mmax, mmin = 0.05,0.2

    # define array of mean waiting times
    means = np.linspace(mmax, mmin,200)

    # loop through setups
    for case, d in fitresd.T.iterrows():

        # get case color
        color = d["color"]

        # get fit parameters
        params = d[list("abcde")].values.astype(float)

        # use parametrization to infer latitudes at 90 deg and 0 deg
        sigs90 = sig(90, means, params)
        plt.plot(means, sigs90, color=color, linestyle="dotted")

        sigs0 = sig(0., means, params)
        plt.plot(means, sigs0, color=color, linestyle="solid")

        # fill area between
        plt.fill_between(means, sigs0, sigs90, color=color, alpha=.2)

        # add legend
        handles.append(Line2D([0], [0], color=color, lw=6, linestyle="solid"))
        if "1 spots" in case:
            case = "1 spot"
        labels.append(case)

    # 90 vs 0 deg legend entries
    for ls, deg in [("solid", 0),("dotted", 90)]:
        handles.append(Line2D([0], [0], color="grey", lw=6, linestyle=ls))
        labels.append(f"{deg} deg")

    # layout
    plt.xlim(mmax, mmin)
    plt.legend(handles, labels, loc=4, frameon=False, fontsize=11)
    plt.tight_layout()

    # labels
    plt.xlabel(r"mean waiting time $\mu$")
    plt.ylabel(r"standard deviation of waiting time $\sigma$")

    # print to file
    path = "plots/parameter_space.png"
    print("Save parameters space figure to: ", path)
    plt.savefig(path, dpi=300)