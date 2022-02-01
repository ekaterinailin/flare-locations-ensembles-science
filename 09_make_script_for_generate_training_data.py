""" 
Script to generate training data.

Ekaterina Ilin 
MIT License (2022)
"""

import numpy as np

from datetime import date, datetime

import sys

from flares.__init__ import (LOG_DATA_OVERVIEW_PATH,
                             SCIPT_NAME_GENERATE_DATA,
                            )

DECOMPFUNCS = ["decompose_ed_randomly_and_using_Davenport",
	           "decompose_ed_from_UCDs_and_Davenport")

if __name__ == "__main__":
  
    today = datetime.now().strftime("%d_%m_%Y_%H_%M")

    # quadratic limd darkening
    u_ld = [0.5079, 0.2239]

    # size of light curve
    size_lc = 2000

    # min and max energy of flares in ED space
    emin, emax = 1e-1, 1e6

    # min and max powerlaw exponent
    alphamin, alphamax = 1.5, 2.5

    # min and max number of flares per lc
    betamin, betamax = 1, 30

    # numbers of spots
    n_spots_min, n_spots_max = 1, 3

    # Gaussian noise level
    errval = 5e-12

    # pick a small but not too small flaring region size
    spot_radius = 0.01

    # pick a latitude width to scatter the spots around a bit
    latwidth = 1e-5

    # total number of light curves given from command line
    n_lcs = int(sys.argv[1])

    # choose random mid latitude or fix it
    midlat = "random"

    # choose decomposition function
    decomposeed = DECOMPFUNCS[1]
    
    # inputs string for log file
    inputs = (f"{u_ld[0]},{u_ld[1]},{emin},{emax},{alphamin},"
              f"{alphamax},{betamin},{betamax},{size_lc},"
              f"{errval},{spot_radius},{midlat},{latwidth},"
              f"{n_spots_min},{n_spots_max},{decomposeed}")
    
    # how many batches
    batches = int(sys.argv[2])

    # -------------------------- TRAINING SET ----------------------------------
    
    # this is where the flare tables go    
    path = f"results/{today}_flares_train.csv"

    # generate script for parallel run

    # number of light curves per core
    n_lcs_per_batch = n_lcs // batches    
    command =  f"python 09_generate_training_data.py {today} {n_lcs_per_batch} {path} train\n"    

    with open(SCIPT_NAME_GENERATE_DATA, "w") as f:
        for i in range(batches):
            f.write(command)   

    with open(LOG_DATA_OVERVIEW_PATH, "a") as f:
        line = (f"{today},train,{path},{inputs},{n_lcs}\n")
        f.write(line)

    # -------------------------- TRAINING SET END ------------------------------


    # -------------------------- VALIDATION SET --------------------------------

    # validation set shall be 10% of the size of the training set
    factor_smaller = 10

    # this is where the flare tables go
    path = f"results/{today}_flares_validate.csv"

    # generate script for parallel run

    # number of light curves per core
    n_lcs_per_batch = n_lcs // batches // factor_smaller  
 
    command =  f"python 09_generate_training_data.py {today} {n_lcs_per_batch} {path} validate\n"    

    with open(SCIPT_NAME_GENERATE_DATA, "a") as f:
        for i in range(batches):
            f.write(command)  

    with open(LOG_DATA_OVERVIEW_PATH, "a") as f:
        line = (f"{today},validate,{path},{inputs},{n_lcs // factor_smaller}\n")
        f.write(line)

    # -------------------------- VALIDATION SET END ----------------------------

