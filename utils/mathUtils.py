# Custom math utilities in python 3
# Henryk T. Haniewicz, 2018

# Imports
import numpy as np

# Functions

def rootMeanSquare( array ):

    '''
    Returns the RMS of a data array
    '''

    rms = np.sqrt( np.mean( np.power( array, 2 ) ) )
    return rms


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
