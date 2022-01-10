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
from decomposeed import decompose_ed_from_UCDs_and_Davenport

from datetime import date, datetime

import sys


if __name__ == "__main__":
    
    today = date.today().strftime("%Y_%m_%d")
    
    u_ld = [0.5079, 0.2239]

    t = np.arange(0, 2 * np.pi, 2 * np.pi/2000)
    phases = t * u.rad

    emin, emax = 1e-1, 1e6

    flc = FlareLightCurve(time=t)
    err = np.full_like(t, 5e-12)
    itmed = np.ones_like(t)

    spot_radius = 0.01
    n_inclinations = 1

    for i in range(int(sys.argv[1])):
        

        # 1-3 spots
        n_spots = np.random.randint(1,4)

        # alpha different for each spot possible
        alpha = - np.random.rand(n_spots) - 1.5

        # flare frequency 1-20 flares per LC 
        beta = np.random.randint(1, 20, size=n_spots)

        # random latitude
        lat = np.random.rand(n_spots) * 90. - 1e-10


        flares = flare_contrast(t, n_spots, [emin] * n_spots, [emax] * n_spots, alpha, beta, 
                                n_inclinations,
                                decompose_ed=decompose_ed_from_UCDs_and_Davenport)


        # make flaring spots
        lons, lats, radii, inc_stellar = generate_spots(lat, lat+1e-10,
                                                        [spot_radius] * n_spots, n_spots,
                                                        n_inclinations=n_inclinations)

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
        flc.detrended_flux = lc + np.random.normal(0,1e-11,len(lc))
        flc.detrended_flux_err = err
        flc.it_med = itmed

        # search for flares
        flares = flc.find_flares().flares

        del flares["cstart"]
        del flares["cstop"]

        # add latitude, inclination
        flares["midlat_deg"] = lats[0,0].value # mid latitude
        flares["inclination_deg"] = inc_stellar[0].value # inclination

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
        
        flares["starid"] = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")


        # if no flares found, skip
        if flares.shape[0]==0:
            continue
        # write results to file 
        else:
            with open(f"results/{today}_flares_alpha_beta_rand_validate.csv", "a") as file:
                flares.to_csv(file, index=False, header=False)
