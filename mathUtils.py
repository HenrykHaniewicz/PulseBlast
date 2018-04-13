# Custom math utilities in python 3
# Henryk T. Haniewicz, 2018

# Imports
import numpy

# Functions

def rootMeanSquare( array ):

    '''
    Returns the RMS of a data array
    '''

    rms = numpy.sqrt( numpy.mean( numpy.power( array, 2 ) ) )
    return rms


def chauvenet( array, mean = 0, stddev = 1, threshold = 3.0 ):

    '''
    Returns a boolean array of the same shape as the input array based on the
    Chauvenet outlier criterion.
    Default values for the mean and stddev are given but it is more useful to use
    values calculates from your array.
    '''

    absDiff = abs( array - mean )

    return absDiff > ( threshold * stddev )


def doubleMAD( vector, threshold = 3.5 ):

    '''
    Returns a boolean array comparing the MZS to the given threshold factor.
    Only works with 1D arrays (vectors) but can be iterated over for multiple distributions.
    A return of True implies an outlying data point.
    '''

    # Calculate the overall median (allows for masked vectors)
    m = numpy.ma.median( vector )

    # Calculate the absolute deviation from the true median
    absDev = numpy.abs( vector - m )

    # Calculate the median absolute deviation for both the left and right splits
    leftMAD = numpy.ma.median( absDev[vector <= m] )
    rightMAD = numpy.ma.median( absDev[vector >= m] )

    vectorMAD = leftMAD * numpy.ones( len( vector ) )
    vectorMAD[vector > m] = rightMAD

    # Calculate the modified Z score
    MZS = 0.6745 * absDev / vectorMAD

    # If the value of the vector equals the median, set the MZS to 0
    MZS[vector == m] = 0

    # Return true if the MZS is greater than the threshold
    return MZS > threshold
