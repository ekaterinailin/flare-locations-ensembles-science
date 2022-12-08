""" 
Python3 - UTF-8

Ekaterina Ilin 
MIT License (2022)

Example script that generates a light curve with flares, 
then modulates it accroding to different incclination angles 
of the star.

"""

import astropy.units as u

from fleck import generate_spots, Star
import numpy as np

from altaipony.altai import aflare
import matplotlib.pyplot as plt

from altaipony.utils import generate_random_power_law_distribution

from flares.flares import flare_contrast


if __name__ == "__main__":

    # energy limits
    emin, emax = 1, 10

    # number of flares
    alpha, beta = -1.6, 10

    # number of spots
    nspots = 1

    # number of inclinations
    n_inclinations = 1

    # mid latitude of the active latitude
    midlat = 80

    # width of the active latitude
    latwidth = 5 #deg

    # spot radius
    spot_radius = 0.01 # Rp/Rstar

    # limb darkening coefficients
    u_ld = [0.5079, 0.2239]

    # init time series
    t = np.arange(0, 2 * np.pi, 2 * np.pi/600) 


    # make light curve
    lc = flare_contrast(t, nspots, [emin] * nspots, [emax] * nspots, alpha, beta, 
                                n_inclinations)

    # generate spots
    lons, lats, radii, inc_stellar = generate_spots((midlat - latwidth / 2.) ,
                                                    (midlat + latwidth / 2.) ,
                                                    spot_radius, nspots,
                                                    n_inclinations=10)
    # make star
    star = Star(spot_contrast=lc, phases=t * u.rad, u_ld=u_ld)

    # make light curves
    lcs = star.light_curve(lons, lats, radii, inc_stellar)
    
    # plot the light curves
    plt.figure(figsize=(12,6))

    # add some offset to the light curves to make them visible
    plt.plot(star.phases/2/np.pi, lcs[:,:] + np.linspace(0,5e-6,lcs.shape[1]))

    # layout and labeling
    plt.xlim(0,1)
    plt.xlabel("stellar rotational phase", fontsize=14)
    plt.ylabel("relative stellar flux", fontsize=14)
    plt.legend(fontsize=15, loc=1, frameon=False);
    plt.title("single flaring spot at 80 deg latitude, at 10 different inclinations",
              fontsize=15)

    # save the plot
    path = "plots/single_flaring_spot_80_deg_lightcurves.png"
    plt.savefig(path, dpi=300)
    print("\nSaved plot to: ", path)
