import pytest
import numpy as np

from ..flares import (wrapped_aflare,
                mock_decompose_ed,
                create_flare_light_curve,
                flare_contrast,
                )

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

