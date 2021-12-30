import numpy as np

from ..decomposeed import (decompose_ed_from_UCDs_and_Davenport,
                           a_from_ed,
                           fwhm_from_ed_a,
                          )

def test_a_from_ed():
    """Some simple shape and NaN checks."""
    
    # if ratio is zero return zero
    assert a_from_ed(0.) == 0.

    # enter NaN, get NaN
    assert np.isnan(a_from_ed(np.nan))

    # shape of array is preserved
    assert a_from_ed(np.linspace(10,100,100)).shape[0] == 100
    
    
    
def test_fwhm_from_ed_a():
    """Some simple shape and NaN checks."""
    
    # if ratio is zero return zero
    assert fwhm_from_ed_a(0.) == 0.

    # enter NaN, get NaN
    assert np.isnan(fwhm_from_ed_a(np.nan))

    # shape of array is preserved
    assert fwhm_from_ed_a(np.linspace(10,100,100)).shape[0] == 100
    
    
    
def test_decompose_ed_from_UCDs_and_Davenport():
    """Some simple shape and NaN checks."""

    # check that NaNs stay NaNs
    assert np.isnan(decompose_ed_from_UCDs_and_Davenport(np.nan)).all()

    # check shapes
    a, fwhm = decompose_ed_from_UCDs_and_Davenport(np.logspace(-2,5,100))
    assert a.shape[0] == 100
    assert fwhm.shape[0] == 100


