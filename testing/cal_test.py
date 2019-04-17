# Cal Test

import numpy as np
import math
from random import *
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.ndimage import map_coordinates

import warnings
#warnings.filterwarnings('error')

from pypulse.archive import Archive
from pypulse.rfimitigator import RFIMitigator
from calculate_flux import getFlux


"""
DONE:
Main logic
Argparsing for frequency
Getting calibrated TOAs


TODO:
Possibly needs to all be done as a class (with argparsing handled in __name__ == "__main__" block)

Smart file name handling (e.g. if PUPPI, filename will be "puppi_{MJD}_{PSR}_*.fits")
    if * contains "cal", it is the cal file of a particular MJD at band, f

Make logic LESS C++ and MORE Pythonic
"""

import argparse
def parser( progname ):

    """
    Initializes argparse and collects the command line arguments.
    Returns a list of input arguments.
    """

    # Initialize the parser
    parser = argparse.ArgumentParser( formatter_class = argparse.RawDescriptionHelpFormatter,
                prog = progname,
                description = '''\
                     PulseBlast Zapping Handler
                -------------------------------------
                   Argument handler for PulseBlast
                        Calibrator and zapping
                    ''' )

    # Arguments list
    parser.add_argument( '-f', '--freq', dest = 'freq_zap', nargs = '*', default = None, help = 'Zap in frequency' )
    parser.add_argument( '-a', '--abs', dest = 'channel_space', action = 'store_true', default = False, help = 'If true, zaps channels. If false, zaps values.' )
    parser.add_argument( '-i', '--ignore', dest = 'ignore', nargs = '*', default = None, type = int, help = 'Set certain dates to be ignored.' )

    args = parser.parse_args()

    return args


def get_AABB_Fcal( dir, continuum_on, continuum_off, args, G = 10.0, T0 = 1.0 ):

    ON, OFF = dir + continuum_on, dir + continuum_off

    if args.freq_zap is not None:
        for i, arg in enumerate( args.freq_zap ):
            args.freq_zap[i] = int( args.freq_zap[i] )


    ar_on, ar_off = Archive( ON, verbose = False ), Archive( OFF, verbose = False )
    rfi_on, rfi_off = RFIMitigator( ar_on ), RFIMitigator( ar_off )
    s_duty_on, s_duty_off = ar_on.getValue( "CAL_PHS" ), ar_off.getValue( "CAL_PHS" )
    duty_on, duty_off = ar_on.getValue( "CAL_DCYC" ), ar_off.getValue( "CAL_DCYC" )
    nchan_on, nchan_off = ar_on.getNchan(), ar_off.getNchan()
    npol_on, npol_off = ar_on.getNpol(), ar_off.getNpol()
    nbin_on, nbin_off = ar_on.getNbin(), ar_off.getNbin()
    BW_on, BW_off = ar_on.getBandwidth(), ar_off.getBandwidth()
    CTR_FREQ_on, CTR_FREQ_off = ar_on.getCenterFrequency( weighted = True ), ar_off.getCenterFrequency( weighted = True )
    for arc in [ ar_on, ar_off ]:
        arc.tscrunch()

    if args.freq_zap is not None:
        if len( args.freq_zap ) == 1:
            if args.channel_space:
                rfi_on.zap_channels( args.freq_zap )
                rfi_off.zap_channels( args.freq_zap )
            else:
                print( "No zapping occurred (tried to zap channels in frequency space). Carrying on with calibration..." )
        elif len( args.freq_zap ) == 2 and not args.channel_space:
            rfi_on.zap_frequency_range( args.freq_zap[0], args.freq_zap[1] )
            rfi_off.zap_frequency_range( args.freq_zap[0], args.freq_zap[1] )
        else:
            rfi_on.zap_channels( args.freq_zap )
            rfi_off.zap_channels( args.freq_zap )


    data_on, data_off = ar_on.getData(), ar_off.getData()


    converted_data_on, converted_data_off = np.empty( 2, dtype = object ), np.empty( 2, dtype = object )
    converted_data_on[0], converted_data_on[1] = IQUV_to_AABB( data_on, basis = "cartesian" )
    converted_data_off[0], converted_data_off[1] = IQUV_to_AABB( data_off, basis = "cartesian" )



    # Initialize the continuum data. SUBINT, POL,
    continuum_on_source, high_on_mean, low_on_mean = np.zeros( ( 2, nchan_on, nbin_on ) ), np.zeros( ( 2, nchan_on ) ), np.zeros( ( 2, nchan_on ) )
    continuum_off_source, high_off_mean, low_off_mean = np.zeros( ( 2, nchan_off, nbin_off ) ), np.zeros( ( 2, nchan_off ) ), np.zeros( ( 2, nchan_off ) )
    f_on, f_off, C0 = np.zeros_like( high_on_mean ), np.zeros_like( high_off_mean ), np.zeros_like( high_off_mean )
    T_sys = np.zeros_like( C0 )
    F_cal = np.zeros_like( T_sys )

    # Load the continuum data
    for i in np.arange( 2 ):
        for j in np.arange( nchan_on ):

            continuum_on_source[i][j], high_on_mean[i][j], low_on_mean[i][j] = prepare_cal_profile( converted_data_on[i][j], s_duty_on, duty_on )
            continuum_off_source[i][j], high_off_mean[i][j], low_off_mean[i][j] = prepare_cal_profile( converted_data_off[i][j], s_duty_off, duty_off )

            f_on[i][j] = ( high_on_mean[i][j] / low_on_mean[i][j] ) - 1
            f_off[i][j] = ( high_off_mean[i][j] / low_off_mean[i][j] ) - 1

            if np.isnan( f_on[i][j] ):
                f_on[i][j] = 1
            if np.isnan( f_on[i][j] ):
                f_off[i][j] = 1

            C0[i][j] = T0 / ( ( 1 / f_on[i][j] ) - ( 1 / f_off[i][j] ) )
            T_sys[i][j] = C0[i][j] / f_off[i][j]
            F_cal[i][j] = ( T_sys[i][j] * f_off[i][j] ) / G     # F_cal has units Jy / cal

            if np.isnan( F_cal[i][j] ):
                F_cal[i][j] = 0


    frequencies_on_off = chan_to_freq( CTR_FREQ_on, BW_on, nchan_on )

    f1, f2 = interp1d(frequencies_on_off, F_cal[0], kind='cubic', fill_value = 'extrapolate'), interp1d(frequencies_on_off, F_cal[1], kind='cubic', fill_value = 'extrapolate')

    return f1, f2


def get_Jy_per_count( dir, psr_cal_file, fitAA, fitBB ):

    file = dir + psr_cal_file

    ar = Archive( file, verbose = False )
    rfi = RFIMitigator( ar )
    ar.tscrunch()
    s_duty = ar.getValue( "CAL_PHS" )
    duty = ar.getValue( "CAL_DCYC" )
    nchan = ar.getNchan()
    npol = ar.getNpol()
    nbin = ar.getNbin()
    BW = ar.getBandwidth()
    data = ar.getData()
    CTR_FREQ = ar.getCenterFrequency( weighted = True )

    converted_data = IQUV_to_AABB( data, basis = "cartesian" )

    frequencies = chan_to_freq( CTR_FREQ, BW, nchan )
    psr_cal, high_psr, low_psr = np.zeros( ( 2, nchan, nbin ) ), np.zeros( ( 2, nchan ) ), np.zeros( ( 2, nchan ) )
    for i in np.arange( 2 ):
        for j in np.arange( nchan ):
            psr_cal[i][j], high_psr[i][j], low_psr[i][j] = prepare_cal_profile( converted_data[i][j], s_duty, duty )

    # Calculate jy_per_count{p, f}
    jy_per_count_factor = np.zeros_like( high_psr )
    # for i in np.arange( 2 ):
    for j in np.arange( nchan ):
        jy_per_count_factor[0][j] = fitAA( frequencies[j] ) / ( high_psr[0][j] - low_psr[0][j] )   # A has units Jy / count

    for j in np.arange( nchan ):
        jy_per_count_factor[1][j] = fitBB( frequencies[j] ) / ( high_psr[1][j] - low_psr[1][j] )   # A has units Jy / count

    return jy_per_count_factor

def find_cal_switching_points( vector, start_duty = 0.0, duty = 0.5 ):

    start = math.floor( len( vector ) * start_duty )

    bin_start = math.floor( len( vector ) * ( start_duty + duty ) )
    bin_end = bin_start + ( math.floor( len( vector ) * duty ) )

    return start, bin_start, bin_end

def prepare_cal_profile( prof, start_duty = 0.0, duty = 0.5, r_err = 8 ):

    profile = prof
    bin_params = find_cal_switching_points( profile, start_duty, duty )

    low_mean = np.mean( profile[ bin_params[0] : bin_params[1] ] )
    high_mean = np.mean( profile[ bin_params[1] : bin_params[2] ] )

    low_mean = round( low_mean, r_err )
    high_mean = round( high_mean, r_err )

    return profile, high_mean, low_mean

def chan_to_freq( ctr_freq, bandwidth, nchan ):

    start_freq = ctr_freq - ( bandwidth / 2 )
    end_freq = ctr_freq + ( bandwidth / 2 )
    freq = np.linspace( start_freq, end_freq, num = nchan )
    return freq

def row_multiply( matrix, vector ):

    """
    Takes a 2D matrix and a 1D vector and multiplies the nth element of 'vector' with the nth row of 'array'
    """

    if matrix.ndim != 2:
        raise ValueError( "Matrix must be 2D" )
    elif vector.ndim != 1:
        raise ValueError( "Vector must be 1D" )

    out_arr = ( matrix.T * vector ).T
    return out_arr


def IQUV_to_AABB( prof, basis = "cartesian" ):
    # Returns the IQUV polarization vectors as square vectors in the basis stated

    if len( prof.shape ) == 4:
        I = prof[:,0]

        if basis is "cartesian":
            comp = prof[:,1]
        elif basis is "rotated":
            comp = prof[:,2]
        elif basis is "circular":
            comp = prof[:,3]
        else:
            raise ValueError( "'basis' must be either 'cartesian', 'rotated' or 'circular'." )
    elif len( prof.shape ) == 3:
        I = prof[0]

        if basis is "cartesian":
            comp = prof[1]
        elif basis is "rotated":
            comp = prof[2]
        elif basis is "circular":
            comp = prof[3]
        else:
            raise ValueError( "'basis' must be either 'cartesian', 'rotated' or 'circular'." )

    aa = np.add( I, comp ) / 2
    bb = np.subtract( I, comp ) / 2

    return aa, bb


def AABB_to_IQUV( prof, basis = "cartesian" ):

    if len( prof.shape ) == 4:
        aa, bb = prof[:,0], prof[:,1]
    elif len( prof.shape ) == 3:
        aa, bb = prof[0], prof[1]

    a, b = np.lib.scimath.sqrt( aa ), np.lib.scimath.sqrt( bb )
    I = np.add( aa, bb )

    if basis is "cartesian":
        Q = np.subtract( aa, bb )
        U = 2 * ( a * ( b.conjugate() ) ).real
        V = -2 * ( a * ( b.conjugate() ) ).imag
    elif basis is "rotated":
        Q = -2 * ( ( a.conjugate() ) * b ).real
        U = np.subtract( aa, bb )
        V = 2 * ( ( a.conjugate() ) * b ).imag
    elif basis is "circular":
        Q = 2 * ( ( a.conjugate() ) * b ).real
        U = -2 * ( ( a.conjugate() ) * b ).imag
        V = np.subtract( aa, bb )
    else:
        raise ValueError( "'basis' must be either 'cartesian', 'rotated' or 'circular'." )

    return I, Q, U, V


def apply_cal_factor_to_prof( dir, psr_file, cal_factor, rfi_mitigation = False, threshold = 3, setdata = True ):

    file = dir + psr_file
    ar = Archive( file, verbose = False )
    if rfi_mitigation:
        rfi_mit = RFIMitigator( ar )
        rfi_mit.zap_minmax( threshold = threshold )

    nchan = ar.getNchan()
    nsub = ar.getNsubint()

    data = ar.getData()
    converted_data_aa, converted_data_bb = IQUV_to_AABB( data, basis = "cartesian" )

    new_converted_aa, new_converted_bb, new_converted, new_data = np.empty( nsub, dtype = object ), np.empty( nsub, dtype = object ), np.empty( nsub, dtype = object ), np.empty( nsub, dtype = object )
    for i, sub in enumerate( np.arange( nsub ) ):
        new_converted_aa[i] = row_multiply( converted_data_aa[i], cal_factor[0] )
        new_converted_bb[i] = row_multiply( converted_data_bb[i], cal_factor[1] )
        new_converted[i] = np.array( (new_converted_aa[i], new_converted_bb[i]) )
        new_data[i] = AABB_to_IQUV( new_converted[i], basis = "cartesian" )

    if setdata:
        ar.setData( new_data )

    return new_data, ar



if __name__ == "__main__":

    args = parser( 'cal_test.py' )

    if args.ignore:
        mjd_ignore_list = args.ignore
    else:
        mjd_ignore_list = []

    T0_430, T0_lbw = getFlux( 0.430, "B1442", False ), getFlux( 1.380, "B1442", False )

    filename = r"/Users/zhn11tau/Documents/PhD/Pulsar Timing/PSR J1829+2456/l_band_sept_oct_2018_nosubband.test"

    import os
    from astropy.io import fits

    temp = np.load( r"/Volumes/Henryk_Data/PSR_J1829+2456/Template Profiles/LbandtemplatePreJune2018.npy" )

    # Directory for continuum
    dir = "/Volumes/Henryk_Data/0737_test_data/"
    dir2 = "/Volumes/Henryk_Data/PSR_J1829+2456/Post_Sept_2018_data/"


    for file in os.listdir( dir2 ):

        print(file)

        fileF = dir2 + file

        # Check if there is a cal file for the file. If not, jy_per_count is an array of ones

        try:
            hdul = fits.open( fileF )
        except OSError:
            print( "File {} did not match ASCII signature required for a fits file".format( file ) )
            continue

        # Get the frequency band used in the observation.
        try:
            frontend = hdul[0].header[ 'FRONTEND' ]
        except OSError:
            print( "Could not find any frontend information in file {}".format( file ) )
            hdul.close()
            continue

        # Get the observation mode.
        try:
            obs = hdul[0].header[ 'OBS_MODE' ]
        except OSError:
            print( "Could not find any observation mode information in file {}".format( file ) )
            hdul.close()
            continue

        if frontend == "lbw":
            if obs == "PSR":
                psr_mjd = hdul[0].header[ 'STT_IMJD' ]
                if psr_mjd in mjd_ignore_list:
                    hdul.close()
                    continue
                try:
                    psr_mjd != cal_mjd
                except NameError:
                    jy_per_count = np.ones( ( 2, hdul[4].header[ 'NCHAN' ] ) )

                hdul.close()

                data, ar = apply_cal_factor_to_prof( dir2, file, jy_per_count, True, 1.0 )
                print("Cal applied correctly")
                ar.pscrunch()
                ar.tscrunch( nsubint = 1 )
                ar.fscrunch( nchan = 1 )
                ar.plot()
                print("Scrunching done")
                exit()

                ar.time( temp, filename = filename, MJD = True, flags = "-f PUPPI_1400", appendto = True )

                print("Timing done")

            elif obs == "CAL":
                cal_mjd = hdul[0].header[ 'STT_IMJD' ]
                if cal_mjd in mjd_ignore_list:
                    hdul.close()
                    continue
                f1, f2 = get_AABB_Fcal( dir, "GUPPI_1442on_55217_0008_cal_0001.fits", "GUPPI_1442off_55217_0007_cal_0001.fits", args, G = 11.0, T0 = T0_lbw )
                jy_per_count = get_Jy_per_count( dir2, file, f1, f2 )
                hdul.close()
            else:
                raise OSError( "What?" )
        else:
            hdul.close()
            continue
