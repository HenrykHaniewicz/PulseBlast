# Custom math utilities in python 3
# Henryk T. Haniewicz, 2018

# Imports
import math
import numpy as np
from custom_exceptions import DimensionError
from scipy.stats import rv_continuous

# PDF classes
class test_dist( rv_continuous ):

    def _pdf( x, a, b, c ):
        return np.sqrt(a) * ( np.exp(-(b*x)**2 / c ) / np.sqrt(2.0 * np.pi) )

class FFT_dist( rv_continuous ):

    def _pdf( x, b, a, k ):
        return (b/(np.sqrt(1 + a*((k-x)**2))))

# Functions
def rootMeanSquare( array ):

    '''
    Returns the RMS of a data array
    '''

    return np.sqrt( np.mean( np.power( array, 2 ) ) )


def rmsMatrix2D( array, mask = None, nanmask = False ):

    '''
    Creates an array of RMS values given a 3D array of data with the first two
    dimensions forming the output matrix and the 3rd dimension containing the
    independent axis.
    '''

    if array.ndim is not 3:
        raise DimensionError( "Input array must be 3 dimensional." )

    width, height, depth = array.shape

    if mask is not None:
        if not isinstance( mask, np.ndarray ):
            raise TypeError( "Mask must be an array." )
        elif mask.ndim is not 1:
            raise DimensionError( "Mask must be an array of dimension 1." )
        elif depth != len( mask ):
            raise ValueError( "Independent dimension and mask must have same length." )

    # Initialize RMS table of zeros
    r = np.zeros( ( width, height ), dtype = float )

    # Initialize the mask array along the 3rd axis
    if mask is None:
        m = np.zeros( depth, dtype = int )
    else:
        m = mask

    # Loop over the other two dimensions
    for i in np.arange( width ):
        for j in np.arange( height ):

            # Calculate the RMS of the array everywhere the mask is 0
            r[i][j] = rootMeanSquare( array[i][j][m == 0] )

            if all( amp == 0 for amp in array[i][j] ):
                r[i][j] = np.nan

    # Mask the nan values in the array for potential plotting if needed
    if nanmask:
        r = np.ma.array( r, mask = np.isnan( r ) )

    # Returns the RMS matrix
    return r


def normalizeToMax( array ):

    '''
    Divides all elements in an array by max value in that column
    '''

    return ( array / ( np.max( array, 0 ) + np.spacing( 0 ) ) )


def chauvenet( array, mean = 0, stddev = 1, threshold = 3.0 ):

    '''
    Returns a boolean array of the same shape as the input array based on the
    Chauvenet outlier criterion.
    Default values for the mean and stddev are for a normalized Gaussian but
    it is more useful to use values calculated from your array.
    '''

    absDiff = abs( array - mean )

    return absDiff > ( threshold * stddev )


def doubleMAD( vector, threshold = 3.5 ):

    '''
    Returns a boolean array comparing the Modified Z-Score (MZS) to the given threshold factor.
    Only works with 1D arrays (vectors) but can be iterated over for multiple distributions.
    A return of True implies an outlying data point.
    '''

    if vector.ndim is not 1:
        raise DimensionError( "Input must be a 1D vector." )

    # Calculate the overall median (allows for masked vectors)
    m = np.ma.median( vector )

    # Calculate the absolute deviation from the true median
    absDev = np.abs( vector - m )

    # Calculate the median absolute deviation for both the left and right splits
    leftMAD = np.ma.median( absDev[vector <= m] )
    rightMAD = np.ma.median( absDev[vector >= m] )

    vectorMAD = leftMAD * np.ones( len( vector ) )
    vectorMAD[vector > m] = rightMAD

    # Calculate the modified Z score
    MZS = 0.6745 * absDev / vectorMAD

    # If the value of the vector equals the median, set the MZS to 0
    MZS[vector == m] = 0

    # Return true if the MZS is greater than the threshold
    return MZS > threshold


# Time handlers
def minutes_to_seconds( minutes, seconds ):
    return ( minutes * 60 ) + seconds

def hours_to_seconds( hours, minutes, seconds ):
    return ( hours * 3600 ) + minutes_to_seconds( minutes, seconds )

def days_to_seconds( days, hours, minutes, seconds ):
    return ( days * 86400 ) + hours_to_seconds( hours, minutes, seconds )

def seconds_to_minutes( seconds, format = False ):
    mins = math.floor( seconds / 60 )
    secs = seconds % 60
    if format:
        output = '{0}m\ {1:.2f}s'.format( mins, secs )
    else:
        output = mins, secs

    return output

def seconds_to_hours( seconds, format = False ):
    hours = math.floor( seconds / 3600 )
    remainder = seconds % 3600
    mins, secs = seconds_to_minutes( remainder )
    if format:
        output = '{0}h\ {1}m\ {2:.2f}s'.format( hours, mins, secs )
    else:
        output = hours, mins, secs

    return output

def seconds_to_days( seconds, format = False ):
    days = math.floor( seconds / 86400 )
    remainder = seconds % 86400
    hours, mins, secs = seconds_to_hours( remainder )
    if format:
        output = '{0}d\ {1}h\ {2}m\ {3:.2f}s'.format( days, hours, mins, secs )
    else:
        output = days, hours, mins, secs

    return output
