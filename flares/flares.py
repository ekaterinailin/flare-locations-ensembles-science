""" 
Flare module. 
`generate_lcs` wraps the module.

Ekaterina Ilin 
MIT License (2022)
"""

import warnings
from os.path import exists

from datetime import datetime

import numpy as np

import astropy.units as u

from altaipony.altai import aflare
from altaipony.utils import generate_random_power_law_distribution

from .decomposeed import (decompose_ed_from_UCDs_and_Davenport,
                         decompose_ed_randomly_and_using_Davenport,
                         )

DECOMPOSEED_DICT = {"decompose_ed_from_UCDs_and_Davenport" : 
                    decompose_ed_from_UCDs_and_Davenport,
                    "decompose_ed_randomly_and_using_Davenport" :
                    decompose_ed_randomly_and_using_Davenport}

from fleck import generate_spots, Star

import matplotlib.pyplot as plt

def get_flares(u_ld, flc, emin, emax, errval, spot_radius, n_inclinations, 
               alphamin, alphamax, betamin, betamax, n_spots_min,
               n_spots_max, midlat, latwidth, decomposeed, path):
    """Generate a light curve of star with parameters drawn from a
    defined distribution.

    Parameters:
    ------------
    u_ld : 2-tuple of floats
        quadratic limb darkening coefficients
    flc : FlareLightCurve
        light curve with t as time series, detrended flux_err=errval, 
        and it_med=1
    emin, emax : float
        minimum and maximum flare energy allowed to be generated
        unit is [s], measured in equivalent duration space
    errval : float
        std of quiescent light curve, used to add Gaussian noise to
        the light curve
    spot_radius : float < 1.
        radius of active region in units of stellar radius
    n_inclinations : int>=1
        number of stars to generate light curves for at random inclinations
    alphamin, alphamax : floats > 0, alphamax > alphamin
        power law index range of flare frequency distribution
    betamin, betamax : ints > 1, betamax > betamin
        power law offset range of flare frequency distribution, number of
        flares in light curve
    n_spots_min, n_spots_max : ints >=1, n_spots_max > n_spots_min
        range of number of spots to be generated in active latitude strip
    midlat, latwidth : float and float or "random", 
	if random: latwidth / 2. < midlat < 90 - latwidth / 2.
        mid latitude and width of active latitude strip
    decomposeed : str
        function string for ED decomposition
    path : str
        path to file
 
    """
    # number of spots, note that randint is [low, high)!
    n_spots = np.random.randint(n_spots_min, n_spots_max + 1)
    
    # alpha different for each spot possible
    alpha = - np.random.rand(n_spots) * (alphamax - alphamin) - alphamin
    
    # number of flares per light curve, note that randint is [low, high)!  
    beta = np.random.randint(betamin, betamax + 1, size=n_spots)
    
    # make flare light curves
    flares = flare_contrast(flc.time.value, n_spots, [emin] * n_spots, [emax] * n_spots, alpha, beta, 
                            n_inclinations,
                            decompose_ed=DECOMPOSEED_DICT[decomposeed])
    
    # pick a random mid-latitude that does go below 0. or above 90.
    if midlat == "random":    
        midlat = np.random.rand() * (90. -  latwidth) + latwidth / 2.
    
    # new on 2022-02-03: pick to place the spot on one of the hemispheres
    sign = np.random.choice([1,-1], size=n_spots)    
        
    # make flaring spots
    lons, lats, radii, inc_stellar = generate_spots(sign * (midlat - latwidth / 2.) ,
                                                    sign * (midlat + latwidth / 2.) ,
                                                    spot_radius, n_spots,
                                                    n_inclinations=n_inclinations)
    # make star! 
    star = Star(spot_contrast=flares, phases=flc.time.value * u.rad, u_ld=u_ld)
    
    # make array in the number of spots size
    betaa = np.array([np.nan] * n_spots_max)
    betaa[:len(beta)] = beta
    
    # make array in the number of spots size
    alphaa = np.array([np.nan] * n_spots_max)
    alphaa[:len(alpha)] = alpha
    
    # make array in the number of spots size
    lonsa = np.array([np.nan] * n_spots_max)
    lonsa[:len(lons)] = lons[:,0].value
    
    # make array in the number of spots size
    latsa = np.array([np.nan] * n_spots_max)
    latsa[:len(lats)] = lats[:,0].value
    

    # get light curve
    lcs = star.light_curve(lons, lats, radii, inc_stellar)
    lc = lcs[:,0]
    
    # define light curve
    flc.flux = lc
    flc.detrended_flux = lc + np.random.normal(0, errval, len(lc))
    
    # search for flares
    flares = flc.find_flares().flares
    print(flares.head().T)
    del flares["cstart"]
    del flares["cstop"]

    
    # add latitude, inclination
    flares["midlat_deg"] = np.abs(lats[0,0].value) # mid latitude
    flares["inclination_deg"] = inc_stellar[0].value # inclination
    
    # save input parameters
    flares["n_spots"] = n_spots
    
    for i in range(n_spots_max):
        flares[f"beta_{i+1}"] = betaa[i]
        flares[f"alpha_{i+1}"] = alphaa[i]
        flares[f"lon_deg_{i+1}"] = lonsa[i]
        flares[f"lat_deg_{i+1}"] = latsa[i]    

    # add identifier for each LC
    flares["starid"] = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
    
      
    # write results to file if any flares were found 
    if flares.shape[0] > 0:
        del flares["total_n_valid_data_points"]
        # write header if necessary, but only once
        file_exists = exists(path)
        if file_exists:
            with open(path, "a") as file:
                flares.to_csv(file, index=False, header=False)
        else:
            with open(path, "a") as file:
                flares.to_csv(file, index=False, header=True)
    
    return flares

def flare_contrast(t, n_spots, emin, emax, alpha, beta, n_inclinations, **kwargs):
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
    kwargs : dict
        keyword arguments to pass to 
        create_flare_light_curve
    
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
                                   t3d, emin, emax, alpha, beta,
                                   **kwargs)
    
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
