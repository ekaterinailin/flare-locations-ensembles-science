""" 
Flare module.

Ekaterina Ilin 
MIT License (2022)
"""

import numpy as np
from altaipony.altai import aflare


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