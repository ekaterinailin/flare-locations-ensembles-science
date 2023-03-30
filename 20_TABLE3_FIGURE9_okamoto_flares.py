import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pyplot

plt.style.use('plots/paper.mplstyle')

from matplotlib.lines import Line2D

import warnings
warnings.filterwarnings('ignore')


def get_latitude(mu, sigma, b0, sb0):
    """Apply Eq. 2 to get latitudes for given waiting time distribution.
    
    Parameters
    ----------
    mu : float
        mean waiting time
    sigma : float
        standard deviation of waiting time
    b0 : list
        fit parameters
    sb0 : list
        fit parameter uncertainties
        
    Returns
    -------
    latitudes : float
        latitude
    """

    # get fit parameters
    a, b, c, d, e = b0
    sa, sb, sc, sd, se = sb0

    # compute thetas
    theta = a * mu**2 + b * mu + c * sigma**2 + d * sigma + e

    # compute uncertainty
    theta_unc = np.sqrt(sa**2 * mu**4 + sb**2 * mu**2 + sc**2 * sigma**4 + sd**2 * sigma**2 + se**2)

    return theta, theta_unc

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


    # -----------------------------------------------------------------------
    # MAKE FIGURE LIKE FIG. 4 BUT WITH REAL DATA ON TOP

    # init figure
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(7,5.5))

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


    # add Okamoto results
    okamoto = pd.read_csv("results/okamoto2021_table.csv")
    okamoto["color"] = ["red","red","red","black"]
    okamoto["marker"] = ["o","d","X","s"]
    okamoto["label"] = [r"$P<10\,$d",r"$5<P<10\,$d",r"$P<5\,$d",r"$P>10\,$d"]


    # make first legend
    legend1 = pyplot.legend(handles, labels, loc=4, frameon=False, fontsize=11)

    # init second legend
    handles, labels = [], []

    # collect results for latitudes
    res_okamoto = {}

    # loop through Okamoto results
    for i, row in okamoto.iterrows():

        res_okamoto[row["label"]] = {}

        # loop through setups with bi- and mono-hem. and 1-5 spots
        for case, d in fitresd.T.iterrows():

            # get fit parameters
            params = d[list("abcde")].values.astype(float)
            sparams = d[[val + "r" for val in list("abcde")]].values.astype(float)

            # get latitudes
            lat, lat_unc = get_latitude(row["mean"], row["std"], params, sparams)

            # if outside boundaries, set to nan, else format with uncertainty
            if (lat < 0) | (lat > 90):
                res_okamoto[row["label"]][case] = np.nan
            else:
                res_okamoto[row["label"]][case] = f"{lat:.0f} [{lat_unc:.0f}]"
    
        # plot data point
        plt.scatter(row["mean"], row["std"], marker=row["marker"], color=row["color"], 
                label=row["sample_ID"], s=150, alpha=0.8, zorder=10)
        
        # add legend entry
        handles.append(Line2D([0], [0], color=row["color"], lw=0,
                            marker=row["marker"], markersize=5))
        labels.append(row["label"])


    # add second legend
    legend2 = pyplot.legend(handles, labels, loc=2, frameon=False, fontsize=11)

    # plot both legends
    ax.add_artist(legend2)
    ax.add_artist(legend1)

    # layout
    plt.xlim(mmax, mmin)
    plt.tight_layout()

    # labels
    plt.xlabel(r"mean waiting time $\mu$")
    plt.ylabel(r"standard deviation of waiting time $\sigma$")

    # print to file
    path = "plots/parameter_space_okamoto2021.png"
    print("Save parameters space figure to: ", path)
    plt.savefig(path, dpi=300)

    # -----------------------------------------------------------------------   
    # SETUP PRINTABLE TABLE WITH RESULTS

    # convert to dataframe
    res_okamoto = pd.DataFrame(res_okamoto)

    # drop empty columns
    res_okamoto.dropna(axis=0, how="all", inplace=True)

    # replace nan with - 
    res_okamoto.replace(np.nan, "-", inplace=True)

    # rename columns and transpose
    res_okamoto = res_okamoto.T.rename(columns=dict(zip(res_okamoto.T.columns,
                            [f"{val} [deg]" for val in res_okamoto.T.columns])))

    # select columns to print
    printdf = okamoto[["label", "min_rot", "max_rot", "mean", "std",
                    "n_stars", "n_flares"]]

    # rename columns
    printdf.rename(columns={"mean":"$\mu$", "std":"$\sigma$"}, inplace=True)

    # shorted mu and sigma to 3 decimals
    printdf[r"$\mu$"] = printdf[r"$\mu$"].round(3)
    printdf[r"$\sigma$"] = printdf[r"$\sigma$"].round(3)

    # convert to int
    printdf[r"$n_{*}$"] = printdf.n_stars.astype(int)
    printdf[r"$n_{f}$"] = printdf.n_flares.astype(int)

    # drop columns
    for col in ["n_stars", "n_flares"]:
        printdf = printdf.drop(col, axis=1)

    # round to two decimals
    printdf[r"$P_{min}$ [d]"] = printdf.min_rot.round(2)
    printdf[r"$P_{max}$ [d]"] = printdf.max_rot.round(2)

    # drop columns
    for col in ["min_rot", "max_rot"]:
        printdf = printdf.drop(col, axis=1)

    # set new index
    printdf.set_index("label", inplace=True)

    # merge printdf with res_okamoto
    printdf = printdf.merge(res_okamoto, left_index=True, right_index=True)


    # ----------------------------------------------------------------------
    # MAKE THE LATEX TABLE

    string = printdf.T.to_latex(index=True, escape=False)
    string = string.replace("1 spots","1 spot")
    string = string.replace("midrule","hline")
    string = string.replace("toprule","hline")
    string = string.replace("bottomrule","hline")
    # string = string.replace("llrrrr","llllll")

    # ----------------------------------------------------------------------
    # WRITE THE LATEX TABLE TO FILE

    print("Save parameters table to: results/okamoto2021_table.tex")
    with open("results/okamoto2021_table.tex", "w") as f:
        f.write(string)

