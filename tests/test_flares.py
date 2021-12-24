import pytest
import numpy as np

from .. import wrapped_aflare

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

