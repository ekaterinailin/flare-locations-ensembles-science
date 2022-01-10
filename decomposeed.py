""" 
ED decomposition into a and FWHM, used in
flare_contrast in flare.py

Ekaterina Ilin 
MIT License (2022)
"""

import numpy as np
import json

# get ED-amplitude relationship
with open("results/a_from_ed.json", "r") as file:
    data = json.load(file)
    
SLOPE_ED_FROM_A = data["slope"]
INTERCEPT_ED_FROM_A = data["intercept"]


# get ED/amplitude-FWHM relationship
with open("results/fwhm_from_ed_a.json", "r") as file:
    data = json.load(file)
    
SLOPE_FWHM_FROM_ED_A = data["slope"]
INTERCEPT_FWHM_FROM_ED_A = data["intercept"]


def fwhm_from_ed_a(ed_a, slope=SLOPE_FWHM_FROM_ED_A,
                   intercept=INTERCEPT_FWHM_FROM_ED_A):
    """Calculate FWHM of flare give ED and amplitude using
    an log-log-linear approximation to the polynomial ED(fwhm)
    relation inferred from Davenport (2014).
    
    Parameters:
    -----------
    ed_a : float or array
        ED divided by amplitude
    slope, intercept : float, float
        best-fit values to the relationship
    
    Return:
    -------
    float or array - FWHM of the flare,
    or t_1/2 in the Davenport (2014) model
    """
    return 10 ** ((np.log10(ed_a) - intercept) / slope)


def a_from_ed(ed, slope=SLOPE_ED_FROM_A, intercept=INTERCEPT_ED_FROM_A):
    """Calculate amplitude of flare given ED using
    an log-log-linear fit to empirical data.
    
    Parameters:
    -----------
    ed : float or array
        ED
    slope, intercept : float, float
        best-fit values to the ED-a relationship
    
    Return:
    -------
    float or array - relative amplitude of the flare,
     """
    return 10 ** ((np.log10(ed) - intercept) / slope)


def decompose_ed_from_UCDs_and_Davenport(ed):
    """Use empirical ED-a relation to get a, then
    Davenport(2014) formulas (1) and (4) integrated
    to infer FWHM.
    
    Parameters:
    ------------
    ed : float or array
        ED of flare
        
    Return:
    -------
    a, fwhm of flare in rel. units and days
    """
    a = a_from_ed(ed)
    fwhm = fwhm_from_ed_a(ed/a)
    return a, fwhm / 60. / 60. / 24.


def decompose_ed_randomly_and_using_Davenport(ed):
    """Take random amplitude between 1e-3 and 100, then
    Davenport(2014) formulas (1) and (4) integrated
    to infer FWHM.
    
    Parameters:
    ------------
    ed : float or array
        ED of flare
        
    Return:
    -------
    a, fwhm of flare in rel. units and days
    """
    ed_ = [ed] if isinstance(ed, float) else ed
    a = np.power(10, np.random.rand(len(ed_)) * 5. - 3.)
    fwhm = fwhm_from_ed_a(ed/a)
    return a, fwhm / 60. / 60. / 24.