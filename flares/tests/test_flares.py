import pytest
import numpy as np

import os

from altaipony.flarelc import FlareLightCurve

from ..flares import (wrapped_aflare,
                      mock_decompose_ed,
                      create_flare_light_curve,
                      flare_contrast,
                      get_flares,
                     )

def test_get_flares():
    """Integration test for sensible parameters with
    both random and fixed mid latitude.
    """
    # --------------- RANDOM MID LATITUDE -------------------
    # -------------------- INPUTS ---------------------------

    # time series in rad
    t = np.linspace(0, 2 * np.pi, 2000)

    # define flare light curve
    flc = FlareLightCurve(time=t)
    flc.detrended_flux_err = 1e-11

    # define input parameters
    n_spots_max = 1
    alpha_min, alpha_max = 1.5, 2.5
    beta_min, beta_max = 1, 20
    latwidth = 5

    # collect the above and fixed inputs
    inputs = [[0.5079, 0.2239], flc, 1, 10000, 1e-11, 
              0.01, 3, alpha_min, alpha_max, 
              beta_min, beta_max, 1, n_spots_max, 
              "random", latwidth, 
              "decompose_ed_from_UCDs_and_Davenport", "testfile"]

    # -------------------- INPUTS END -----------------------

    # ------------------- CALL FUNCTION ---------------------

    # get flares    
    flares = get_flares(*inputs)

    # ----------------- CALL FUNCTION END -------------------

    # ----------------- RUN TESTS -------------------

    # 12 general flare and lc properties and 4 spot specific ones
    assert len(flares.columns) == 4 * n_spots_max + 12

    # some properties should be the same for all flares
    for col in ["midlat_deg", "inclination_deg", "n_spots", "starid"]:
        assert (flares[col].values == flares[col].values[0]).all()

    # check spot specific properties
    for i in range(n_spots_max):
        # alpha should stay within margins
        assert (flares[f"alpha_{i+1}"].values < -alpha_min).all()
        assert (flares[f"alpha_{i+1}"].values > -alpha_max).all()

        # beta should stay within margins
        assert (flares[f"beta_{i+1}"].values > beta_min).all()
        assert (flares[f"beta_{i+1}"].values < beta_max).all()

        # lon should stay within margins
        assert (flares[f"lon_deg_{i+1}"].values > 0).all()
        assert (flares[f"lon_deg_{i+1}"].values < 360).all()

        # lat should stay within margins
        assert (np.abs(flares[f"lat_deg_{i+1}"].values) > latwidth / 2.).all()
        assert (np.abs(flares[f"lat_deg_{i+1}"].values) < 90. - latwidth / 2.).all()


        # spot properties are either the same for all flares or NaN
        for col in ["beta","alpha","lon_deg","lat_deg"]:
            assert ((flares[f"{col}_{i+1}"].values == 
                     flares[f"{col}_{i+1}"].values[0]).all() |
                    flares[f"{col}_{i+1}"].isnull().all())

    # it shouldn't recover more flares than were put in:
    assert flares.shape[0] < n_spots_max * beta_max

    # --------------- RUN TESTS END -----------------



    # -------------- FIXED MID LATITUDE --------------

    # change random to fixed value in deg
    midlat = 30.
    inputs[13] =  midlat

    # get flares    
    flares = get_flares(*inputs)

    # check latitudes 
    for i in range(n_spots_max):
        # lat should stay within margins
        assert (np.abs(flares[f"lat_deg_{i+1}"].values) > midlat - latwidth / 2.).all()
        assert (np.abs(flares[f"lat_deg_{i+1}"].values) < midlat + latwidth / 2.).all()

    # -------------- FIXED MID LATITUDE END ------------


    # clean up
    os.remove("testfile")



def test_flare_contrast1():
    """Test #1. Integration and unit tests with either
    multiple or a single spot. Check mostly if 
    units are conserved. Test #2 goes for more 
    dimension checks."""
    
    # MULTIPLE SPOTS
    # give inputs as arrays
    t = np.arange(0, 2 * np.pi, 2 * np.pi/600) 
    n_inclinations = 100
    n_spots = 2
    alpha = [-1.6] * n_spots
    beta = [20] * n_spots
    emin = [1] * n_spots
    emax = [100] * n_spots


    # generate lcs
    flares = flare_contrast(t, n_spots, emin, emax, alpha, beta, n_inclinations)

    # check the shape given the inputs
    assert flares.shape == (len(t), n_spots,n_inclinations)

    # minimum flux should be larger or equal 1, i.e. the quiescent level
    assert np.min(flares) >= 1.

    # in n_spots is a weird float override and mention:
    mywarning = ("Number of spots not an integer. "
                     "Value will be floored to next integer.")
    with pytest.warns(UserWarning, match=mywarning):
        flare_contrast(t, 2.3, emin, emax, alpha, beta, n_inclinations)
        

    # ONE SPOT
    # generate lcs from floats with n_spots==1
    n_spots = 1
    flares = flare_contrast(t, n_spots, 1, 10, -2, 30, n_inclinations)

    # check the shape given the inputs
    assert flares.shape == (len(t), n_spots, n_inclinations)

    # minimum flux should be larger or equal 1, i.e. the quiescent level
    assert np.min(flares) >= 1.
    
    
@pytest.mark.parametrize("n_spots,emin,emax,alpha,beta",
                         [(1, [1, 1], [1], [-2], [2]),
                          (1, [1], [1, 1], [-2], [2]),
                          (1, [1], [1], [-2, 2], [2]),
                          (1, [1], [1, 1], [-2], [2, 3]),
                          ])

def test_flare_contrast2(n_spots, emin, emax, alpha, beta):
    """Test #2. Make sure function crashed if the 
    dimensions don't match. Test #1 has more unit tests
    and also integration tests."""
    
    # generate time array to be the same for all
    t = np.arange(0, 2 * np.pi, 2 * np.pi/600)
    
    # raise IndexError if dimensions don't match
    with pytest.raises(ValueError) as e:
        flare_contrast(t, n_spots, emin, emax, alpha, beta, 5)
        assert e == (f"Check inputs: one or multiple of emin, "
                     f"emax, alpha, beta don't match in size, "
                     f"which should be {int(np.floor(n_spots))}.")


def test_create_flare_light_curve():
    """This basically call two functions that are
    individually tested elsewhere: wrapped_aflare and 
    generate_random_power_law_distribution.
    """
    # set up time array
    time = np.linspace(0,1,1000)

    # create a flare lc
    lc = create_flare_light_curve(time, 0.1, 1000, -2, 2)
    
    # just make sure the shape of the light curve is preserved
    assert lc.shape == time.shape

    

def test_mock_decompose_ed():
    """Test both a float and an array input."""
    # pass an array
    inputvals = np.array([3., 300., 3000.])
    a, fwhm = mock_decompose_ed(inputvals)

    # shape preserved
    assert a.shape[0] == 3
    assert fwhm.shape[0] == 3

    # dont't mess with the default values!
    assert (fwhm == 0.01).all()
    assert (a == inputvals/100.).all()

    # pass a float
    a, fwhm = mock_decompose_ed(3.)

    # shape must be that of a 1D array
    assert a.shape[0] == 1
    assert fwhm.shape[0] == 1

    # dont't mess with the default values!
    assert fwhm[0] == 0.01
    assert a[0] == 0.03

def test_wrapped_aflare():
    """Integration tests only.
    If something goes wrong unit test wise,
    it's most likely on the aflare level.
    """
    # create time array
    time = np.linspace(0, 1, 1000)
    
    # wrap a flare three times
    wt, flare = wrapped_aflare(time, .9, 0.2, 0.4)
    assert wt == 3 # number of wraps
    assert flare[0] >.15 # amplitude at wrapped index
    assert flare.all() > 0. # all phases are exposed to flare
    assert time.shape[0] == flare.shape[0] # size preserved

    # a flare that does not need to be wrapped
    wt, flare = wrapped_aflare(time, .1, 0.01, 0.4) 
    assert wt == 1 # not wrapped
    assert flare[-1] < 0.001 # because defaul threshold is not hit
    assert flare[0] == 0. # therefore not all phases are exposed to flare
    assert time.shape[0] == flare.shape[0] # size preserved

