""" 
Python3.8 -- UTF-8

Ekaterina Ilin 
MIT License (2022)

Script to create night length distribution as a function of latitude.

PRODUCES FIGURE 1 IN THE PAPER
"""

import numpy as np
import matplotlib.pyplot as plt


def daylength(theta, i):
   
    if theta >= i:
        return 1
    elif ((theta<0) & (np.abs(theta) >=i)):
        return 0
    else:
        return np.arccos(-np.tan(theta) * np.tan(np.pi/2-i)) / np.pi


if __name__ == "__main__":


    # set up latitudes and inclinations
    theta = np.linspace(0, np.pi/2, 400)
    i = np.arccos(np.random.rand(3000))
   
    # calculate night lengths for all inclinations and latitudes
    ts = []
    ms = []
    for t in theta:
        dls = []
        for i_ in i:
            dls.append(1 - daylength(t, i_))
        ts.append(np.std(np.array(dls)))
        ms.append(np.mean(np.array(dls)))

    # convert theta to deg
    theta = theta * 180 / np.pi
    nl_plus_std = np.array(ms) + np.array(ts)
    nl_minus_std = np.array(ms) - np.array(ts)

    # plot the results
    plt.figure(figsize=(7,5.5))
    plt.plot(theta, ms, linewidth=3,)
    plt.fill_between(theta, nl_plus_std, nl_minus_std, linewidth=3,
                    label="standard deviation of night length",
                    fontsize=12)

    # layout
    plt.xlim(90,0)
    plt.legend(loc=2)
    plt.xlabel("active latitude [deg]")
    plt.ylabel("mean night length [rotational period]",fontsize=14.5)

    # save the figure
    path = "plots/night_length_and_std.png"
    plt.savefig(path, dpi=300)
    print("\nFigure saved to: ", path)