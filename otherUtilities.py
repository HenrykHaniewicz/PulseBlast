# Extra utilities for pulsars
# Mostly done by R. Ferdman in Python 2 (hence the transpose here to Python 3)

# Imports
import numpy as np
import math
import mathUtils as mu

# Functions


# Routine that creates a mask (of 1s and 0s) to denote which parts of the profile are off and on-peak, respectively
def binMask( profData, duty, threshFactor = 2.0 ):

# Get various values and bins of inpute profile
     nBin = len( profData )
     profSort = profData[profData.argsort()]
     iMid = int( math.floor( 0.5*duty*nBin+0.5 ) )
     profMid = profSort[iMid - 1]
     profPeak = profSort[nBin - 1]

# Get rms of lowest iMid bins of profile

     rms = mu.rootMeanSquare( profSort[0:iMid] )

# Determine number of nearest neighbours to use
     nCheck = nBin / 128
     if ( nCheck < 2 ):
          nCheck = 2

     nTest = ( nCheck / 2 ) - 1

# Cycle through each bin, compare it to its neighbours, and determine whether it can be considered to be off-pulse

# First make a vector of 1s and 0s, depending on how each bin value compares to the midpoint value
     mask = np.ones_like( profData, dtype=np.int8 )

     bigCondition = ( ( profData - profMid ) > ( threshFactor*rms ) )

     '''First create array of profile array nearest neighbour elements, to see if each element will pass criteria for masking, 
     and change corresponding mask array element if so. '''
     for iBin in range( nBin ):
          if ( iBin < nCheck ):
               iTest = np.append( np.arange( nBin - nCheck + iBin, nBin, dtype = np.int8 ), np.arange( 0, iBin + nCheck + 1, dtype = np.int8 ) )
          elif ( iBin > nBin-nCheck - 1 ):
               iTest = np.append( np.arange( iBin - nCheck, nBin, dtype = np.int8 ), np.arange( 0, nCheck - ( nBin - iBin ) + 1, dtype = np.int8 ) )
          else:
               iTest = np.arange( iBin - nCheck, iBin + nCheck + 1, dtype = np.int8 )


          ''' extract() elements of array where bigCondition is true, get length and compare to nTest.  
          If profData is not over threshold, then it is part of off-pulse region so mask it. '''

          nThresh = len( np.extract( bigCondition[iTest], profData[iTest] ) )
          if( nThresh > nTest ):
               mask[iBin] = 0

     return mask


def binMaskFromTemplate( template ):

    '''
    Creates a mask of the profile data based on a template. Returns a 1D
    binary array of length nBin where 0 is the off-pulse region and 1 is the
    on-pulse region.
    '''

    mask = binMask( template, 0.55 )

    return mask


def getBase( profData, duty ):
     
     # get profile mask to determine off-pulse bins
     mask = binMask( profData, duty )
     
     # select those with mask == 0, i.e. baseline bins
     baseline = profData[mask == 0]
     
     # get mean and rms of baseline
     baseMean = np.mean( baseline )
     baseRMS = mu.rootMeanSquare( baseline )

     # return tuple consisting of baseline, mean and rms
     return baseline, baseMean, baseRMS


def removeBase( profData, duty ):

     baseline, baseMean, baseRMS = getBase( profData, duty )

     # remove baseline mean from profile in place
     profData = profData - baseMean

     return profData
