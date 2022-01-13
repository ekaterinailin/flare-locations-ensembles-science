""" 
Script to generate training data.

Ekaterina Ilin 
MIT License (2022)
"""

import numpy as np

import astropy.units as u

from fleck import generate_spots
from fleck import Star

from altaipony.flarelc import FlareLightCurve

from flares import flare_contrast
from decomposeed import (decompose_ed_from_UCDs_and_Davenport,
                         decompose_ed_randomly_and_using_Davenport,
                         )

from datetime import date, datetime

import sys


def generate_lc(u_ld, t, phases, emin, emax, flc, err,
                itmed, spot_radius, n_inclinations, alphamin,
                alphamax, betamin, betamax, n_spots_min,
                n_spots_max, midlat, latwidth, errval, path):
    
    # number of spots, note that randint is [low, high)!
    n_spots = np.random.randint(n_spots_min, n_spots_max + 1)
    
    # alpha different for each spot possible
    alpha = - np.random.rand(n_spots) * (alphamax - alphamin) - alphamin
    
    # number of flares per light curve, note that randint is [low, high)!  
    beta = np.random.randint(betamin, betamax + 1, size=n_spots)
    
    # make flare light curves
    flares = flare_contrast(t, n_spots, [emin] * n_spots, [emax] * n_spots, alpha, beta, 
                            n_inclinations,
                            decompose_ed=decompose_ed_randomly_and_using_Davenport)
    
    
    # make flaring spots
    lons, lats, radii, inc_stellar = generate_spots(midlat - latwidth / 2. , midlat + latwidth / 2. ,
                                                    [spot_radius] * n_spots, n_spots,
                                                    n_inclinations=n_inclinations)
    # make star!
    star = Star(spot_contrast=flares, phases=t * u.rad, u_ld=u_ld)
    
    # make size 3 array
    betaa = np.array([np.nan] * 3)
    betaa[:len(beta)] = beta
    
    # make size 3 array
    alphaa = np.array([np.nan] * 3)
    alphaa[:len(alpha)] = alpha
    
    # make size 3 array
    lonsa = np.array([np.nan] * 3)
    lonsa[:len(lons)] = lons[:,0].value
    
    # get light curve
    lcs = star.light_curve(lons, lats, radii, inc_stellar)
    lc = lcs[:,0]
    
    # define light curve
    flc.flux = lc
    flc.detrended_flux = lc + np.random.normal(0, errval, len(lc))
    flc.detrended_flux_err = err
    flc.it_med = itmed
    
    # search for flares
    flares = flc.find_flares().flares
    
    del flares["cstart"]
    del flares["cstop"]
    
    # add latitude, inclination
    flares["midlat_deg"] = lats[0,0].value # mid latitude
    flares["inclination_deg"] = inc_stellar[0].value # inclination
    
    # save input parameters
    flares["n_spots"] = n_spots
    
    flares["beta_1"] = betaa[0]
    flares["beta_2"] = betaa[1]
    flares["beta_3"] = betaa[2]
    
    flares["alpha_1"] = alphaa[0]
    flares["alphaa_2"] = alphaa[1]
    flares["alpha_3"] = alphaa[2]
    
    flares["lons_1"] = lonsa[0]
    flares["lons_2"] = lonsa[1]
    flares["lons_3"] = lonsa[2]
    
    # add identifier for each LC
    flares["starid"] = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
    
    
    # if no flares found, skip
    if flares.shape[0]==0:
        continue
    # write results to file 
    else:
        with open(path, "a") as file:
            flares.to_csv(file, index=False, header=False)

if __name__ == "__main__":
    
    today = datetime.now().strftime("%d_%m_%Y_%H_%M")

    # quadratic limd darkening
    u_ld = [0.5079, 0.2239]

    # time series in rad
    t = np.arange(0, 2 * np.pi, 2 * np.pi / 2000)
    phases = t * u.rad

    # min and max energy of flares in ED space
    emin, emax = 1e-1, 1e6

    # min and max powerlaw exponent
    alphamin, alphamax = 1.5, 2.5

    # numbers of spots
    n_spots_min, n_spots_max = 1, 3

    # define flare light curve
    flc = FlareLightCurve(time=t)

    # Gaussian noise level
    errval = 5e-12

    # error series kept constant to save computational time
    # is correct per definition, even somewhat more correct
    # than doable in practice
    err = np.full_like(t, errval)

    # the quiescent median is one 
    itmed = np.ones_like(t)

    # pick a small but not too small flaring region size
    spot_radius = 0.01

    # pick a latitude width to scatter the spots around a bit
    latwidth = 1e-5

    # pick a random mid-latitude that does go below 0. or above 90.
    midlat = np.random.rand() * (90. -  latwidth) + latwidth / 2.

    # total number of light curves given from command line
    n_lcs = int(sys.argv[1])

    inputs = (u_ld, t, phases, emin, emax, flc, err,
              itmed, spot_radius, 1, alphamin, # n_inclinations is set to 1 to get each light curve separately
              alphamax, betamin, betamax, n_spots_min,
              n_spots_max, midlat, latwidth, errval)
    
    string = (f"{u_ld[0]},{u_ld[1]},{emin},{emax},{alphamin},"
              f"{alphamax},{betamin},{betamax},{len(t)},"
              f"{errval},{spot_radius},{midlat},{latwidth}")
    
    path = f"results/{today}_flares_train.csv"
    for i in range(n_lcs):
        generate_lc(*inputs, path)

    with open("results/overview_synthetic_data.csv", "a") as f:
        line = (f"{today},train,{path},{string},{n_lcs}\n")
        f.write(line)

    factor_smaller = 10
    path = f"results/{today}_flares_validate.csv"
    for i in range(n_lcs // factor_smaller):
        generate_lc(*inputs, path)

    with open("results/overview_synthetic_data.csv", "a") as f:
        line = (f"{today},validate,{path},{string},{n_lcs // factor_smaller}\n")
        f.write(line)
