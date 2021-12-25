""" 
Flare module.

Ekaterina Ilin 
MIT License (2022)
"""

import warnings

import numpy as np

from altaipony.altai import aflare
from altaipony.utils import generate_random_power_law_distribution


def flare_contrast(t, n_spots, emin, emax, alpha, beta, n_inclinations):
    """Creates a set of flaring light curves.
    
    Parameters:
    -----------
    t : np.array
        array of phases in [0,1]
    n_spots : int >=1
        number of flaring spots, i.e. active regions
    emin : list of floats
        len(emin)=n_spots
        minimum energy that the spot can produce 
        OR detection limit, in ED space
    emax : list of floats
        len(emax)=n_spots
        maximum energy that the
        spot can produce, in ED space
    alpha : list of floats
        len(alpha)=n_spots
        FFD power law exponent, in ED space
    beta : list of floats
        len(beta)=n_spots
        FFD power law offset, in ED space
    n_inclinations : int
        i.e., number of stars
    
    Return:
    --------
    np.ndarray with dimensions (len(t), n_spots, n_inclinations),
    i.e., a matrix of n_spots x n_inclination flare light curves
    of length len(t), each with quiescent flux=1
    """
    
    # Check if number of spots is int
    # If not, warn user:
    if type(n_spots) != int:
        warnings.warn("Number of spots not an integer. "
                      "Value will be floored to next integer.")
    
    
    # expand the time series to the number of spots
    t2d = np.repeat(np.array([t]), repeats=n_spots, axis=0)
                    
    # expand the time series to the number of stars
    t3d = np.repeat(t2d.T[:,:,np.newaxis], repeats=n_inclinations, axis=2)
    
    # define a nested function to wrap the 3d array
    def apply_per_spot(t3d, emin, emax, alpha, beta):
        # create a flare light curve for each star
        # with the same flaring region parameters
        return np.apply_along_axis(create_flare_light_curve, 0,
                                   t3d, emin, emax, alpha, beta)
    
    # if floats are passed, make list
    listify = lambda a: [a] if (isinstance(a, float) | isinstance(a, int)) else a
    emin, emax, alpha, beta = listify(emin), listify(emax), listify(alpha), listify(beta)
    
    # Check dimensions. If they don't fit, throw error:
    if ~(np.array([len(alpha), len(emin), len(emax), len(beta)]) == int(np.floor(n_spots))).all():
        raise ValueError(f"Check inputs: one or multiple of emin, emax, alpha, beta"
                         f" don't match in size, which should be {int(np.floor(n_spots))}.")
    
    # apply function above for each spot
    flares =  np.array([apply_per_spot(t3d[:,i,:], emin[i], emax[i],
                                       alpha[i], beta[i]) for i in range(t3d.shape[1])])
    
    # transpose to make it ready to be passed to 
    # Star.light_curve
    return np.transpose(flares, (1, 0, 2))


def mock_decompose_ed(ed, afactor=100., fixed_fwhm=.01):
    """Take ED of a flare and return
    a fake split in amplitude and FWHM.
    Amplitude is actually nearly linear.
    FWHM has much more spread.
    
    Parameters:
    -----------
    ed : float
        ED of a flare
    afactor : float, default 100
        divide by afactor to convert ED 
        to amplitude
    fixed_fwhm : float, default .01
        fix FWHM to something shorter
        than the full phase, i.e. 1
        
    Return:
    -------
    amplitude, FWHM - float, float
    """
    # turn into array if just float
    if type(ed) is float:
        ed = np.array([ed])
    
    # divide ed by scale factor to get amplitude
    # fix fwhm to something short
    return ed / afactor, np.full_like(ed, fixed_fwhm)




def create_flare_light_curve(time, emin, emax, alpha, beta, 
                             decompose_ed=mock_decompose_ed, **kwargs):
    """Generate a flare light curve using the flare
    model from Davenport(2014) and power law disributed
    flare energies.
    
    Parameters:
    -----------
    time : np.array
        time series
    emin : float
        minimum energy that the spot can produce 
        OR detection limit, in ED space
    emax : float
        maximum energy that the
        spot can produce, in ED space
    alpha : float
        FFD power law exponent, in ED space
    beta : float
        FFD power law offset, in ED space
    decompose_ed : func
        function that takes ED and returns
        amplitude and FWHM of the flare.
        Default at the moment: mock function
        mock_decompose_ed to be replaced later
    kwargs : dict
        keyword arguments to pass to decompose_ed
        
    Return:
    --------
    np.array with the same length as time, that is a light curve
    that contains a number of flares specified by the input parameters
    in relative flux units
    """
    # generate power law distributed flare energies
    EDs = generate_random_power_law_distribution(emin, emax, alpha+1, beta)
    
    # generate start times of flare randomly
    tstart = (np.random.rand(len(EDs)) * (time[-1] - time[0])) + time[0]
    
    # decompose ED
    a, fwhm = decompose_ed(EDs, **kwargs)
    
    # generate each flare and sum up the flux. 
    # Add 1 as baseline, because the amplitude is given in relative units
    lc = (np.array([wrapped_aflare(time, tstart[i], fwhm[i], a[i])[1] for i, ed in enumerate(EDs)]).sum(axis=0) + 1.)
    
    return lc



def wrapped_aflare(time, tstart, fwhm, a, a_threshold=0.001):
    """Wrap flare light curve around phase 1 to 0 
    if flare is cut off at the end of the light curve 
    with an amplitude above a_threshold.
    
    Parameters:
    -----------
    time : np.array of floats
        time series, understood as
        covering phases 0 to 1 of 
        a rotation period
    tstart : float
        start time of flare. If tstart is outside
        the time array, the flare might not 
        appear in the light curve
    fwhm : float > 0
        FWHM of flare as per
        Davenport(2014) model
    a : float > 0
        amplitude of flares as per
        Davenport(2014) model
    a_threshold : float>0
        amplitude threshold. If the light curve
        exceeds this value at the end of the light curve
        it is wrapped back to the beginning.
    
    Return:
    -------
    Number of wrapping iterations + 1
    
    Light curve of length of time with 
    Davenport (2014) flare, but
    wrapped around phase 1 to 0.
    
    """
    # generate the flare
    flare = aflare(time, tstart, fwhm, a)
    
    # check if wrapping is needed
    if flare[-1] > a_threshold:
        
        # copy time array
        time_ = np.copy(time)
        
        # init number of wrap_times
        wrap_times = 1
        
        # iterate until threshold is hit
        while flare[-1] > a_threshold:

            # extend time array
            time_ = time_[-len(time):] + time[-1]
       
            # add flare tail
            flare = np.concatenate([flare, aflare(time_, tstart, fwhm, a)])
         
            # increment number of wraps
            wrap_times += 1
         
        # stack flare back to original light curve size
        return wrap_times, flare.reshape((wrap_times, len(time))).sum(axis=0)
    
    # if wrapping not needed
    else:
        
        # return back original flare 
        return 1, flare