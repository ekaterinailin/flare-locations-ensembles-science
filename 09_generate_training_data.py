import numpy as np
import pandas as pd

from altaipony.flarelc import FlareLightCurve

from flares.flares import get_flares
from flares.decomposeed import 

import sys

if __name__ == "__main__":

    # ---------------- COMMAND LINE INPUT PARAMETERS ---------------------------

    # timestamp for this dataset
    tstamp = sys.argv[1]
    
    # number of lcs in batch
    n_lcs = int(sys.argv[2])

    # table of flares to store the results in
    outpath = sys.argv[3]

    # either train or validate
    typ = sys.argv[4]

    # ---------------- COMMAND LINE INPUT PARAMETERS END -----------------------


    # -------------------- LOG FILE INPUT PARAMETERS ---------------------------

    # read log file with input parameters
    df = pd.read_csv(LOG_DATA_OVERVIEW_PATH)

    # pick the right row and make sure all identifiers fit!
    # only n_lcs does not fit because we are dealing with batches here
    row = df[(df.typ == typ) &
             (df.tstamp == tstamp) &
             (df.outpath == outpath)]

    # ------------------ LOG FILE INPUT PARAMETERS END -------------------------


    # --------------------- DERIVED INPUT PARAMETERS ---------------------------

    # time series in rad
    t = np.arange(0, 2 * np.pi, 2 * np.pi / row.size_lc)

    # define flare light curve
    flc = FlareLightCurve(time=t)

    # error series kept constant to save computational time
    # is correct per definition, even somewhat more correct
    # than doable in practice
    err = np.full_like(t, row.errval)
    flc.detrended_flux_err = err

    # the quiescent median is one 
    itmed = np.ones_like(t)
    flc.it_med = itmed

    # generate only one lc per iteration to make code less complicated
    n_inclinations = 1

    # ------------------- DERIVED INPUT PARAMETERS END -------------------------


    # ---------------------- RUN LOOP WITH INPUTS ------------------------------

    inputs = ((u_ld_0, u_ld_1), flc, row.emin, row.emax, row.errval,
              row.spot_radius, n_inclinations,row.alphamin, row.alphamax,
              row.betamin, row.betamax, row.n_spots_min, row.n_spots_max, 
              row.midlat, row.latwidth, row.decomposeed, outpath)

    for i in range(n_lcs):
        get_flares(*inputs)

    # --------------------- RUN LOOP WITH INPUTS END ---------------------------
