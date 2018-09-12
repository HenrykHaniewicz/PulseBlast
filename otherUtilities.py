# Extra utilities for pulsars and other stuff

# Imports
import numpy as np
import math
import os
import sys
import platform
import mathUtils as mu

# Functions

# Routine that creates a mask (of 1s and 0s) to denote which parts of the
# profile are off and on-peak, respectively
def binMask( profData, duty, threshFactor = 2.0 ):

# Get various values and bins of inpute profile
     nBin = len( profData )
     profSort = profData[profData.argsort()]
     iMid = int( math.floor( 0.5*duty*nBin+0.5 ) )
     profMid = profSort[iMid - 1]
     profPeak = profSort[nBin - 1]

# Get rms of lowest i_mid bins of profile
# Remember in python the second index doesn't need the "-1" there
     #rms = np.std(profSort[0:iMid])
     rms = mu.rootMeanSquare( profSort[0:iMid] )

# Determine number of nearest neighbours to use
     nCheck = nBin/128
     if ( nCheck < 2 ):
          nCheck = 2

     nTest = nCheck/2 - 1

# Now cycle through each bin, compare it to its neighbours, and determine
# whether it can be considered to be off-pulse

# First make a vector of 1s and 0s, depending on how each bin value compares
# to the midpoint value
    # big = np.zeros(n_bin, dtype='int') # start with array of zeros
     mask = np.ones_like( profData, dtype=np.int8 )

     bigCondition = ( ( profData - profMid ) > ( threshFactor*rms ) )

     # First create array of profile array nearest neighbour elements, to see if
     # if each element will pass criteria for masking, and change
     # corresponding mask array element if so.
     for iBin in range( nBin ):
          if ( iBin < nCheck ):
               iTest = np.append(np.arange(nBin-nCheck+iBin,nBin, dtype=np.int8), np.arange(0,iBin+nCheck+1, dtype=np.int8))
          elif ( iBin > nBin-nCheck-1 ):
               iTest = np.append(np.arange(iBin-nCheck,nBin, dtype=np.int8), np.arange(0,nCheck-(nBin-iBin)+1, dtype=np.int8))
          else:
               iTest = np.arange(iBin-nCheck,iBin+nCheck+1, dtype=np.int8)


          # extract() elements of array where big_condition is true, get length
          # and compare to n_test.  If prof_data is not over threshold, then it
          # is part of off-pulse region.  Otherwise, mask it.

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
     # select those with mask==0, i.e. baseline bins
     baseline = profData[mask == 0]
     # get mean and rms of baseline
     baseMean = np.mean( baseline )
     #baseRMS = np.std( baseline )
     baseRMS = mu.rootMeanSquare( baseline )

     # return tuple consisting of mean and rms of baseline
     return baseMean, baseRMS


def removeBase( profData, duty ):

     baseline, baseRMS = getBase( profData, duty )

     # remove baseline mean from profile in place
     profData = profData - baseline

     return profData


def restart_line():
     sys.stdout.write( '\r' )
     sys.stdout.flush()

def display_status( iteration, MAX_ITER ):
    restart_line()

    sys.stdout.write('{0:<10d}[{1:>3d}%]'.format( iteration, int( 100 * float( iteration )/float( MAX_ITER ) ) ) )
    sys.stdout.flush()

# Checks if 'file' has extension 'ext' and, if not, adds it.
def addExtension( file, ext ):
    if not isinstance( ext, str ):
        raise TypeError( "Extension must be a string" )

    # Split the filename up into a root and extension
    root, end = os.path.splitext( file )

    # If file extension does not exist, add the extension
    if not end:
        end = '.' + ext
        fileout = root + end
    else:
        fileout = file

    return fileout


# Formats directories from UI to console
def formatMultipleDirectories( args ):
    if platform.system() == 'Darwin' or 'Linux':
        dirs = ' '.join( args )
        dirs = dirs.replace( ":", "," )
        dirs = dirs.replace( "Macintosh HD", "" )
        dirs = dirs.split( "," )

    elif platform.system() == 'Windows':
        dirs = args

    else:
        raise OSError( "Could not determine OS." )

    return dirs


def addMultipleDirectoryEndSeparators( dirs, shell ):
    if shell == 'Unix':
        for i, d in enumerate( dirs ):
            if not d.endswith("/"):
                dirs[i] += "/"

    elif shell == 'Windows':
        for i, d in enumerate( dirs ):
            if not d.endswith("\\"):
                dirs[i] += "\\"

    else:
        raise ValueError( "Shell not recognized. (Shell provided: {})".format( shell ) )

    return dirs


# Takes in a single directory followed by the rest in a list. I'm gonna change this...
def addDirectoryEndSeparators( dir, dirs ):
    if platform.system() == 'Darwin' or "Linux":
        directory = dir + "/"
        directories = addMultipleDirectoryEndSeparators( dirs, 'Unix' )

    elif platform.system() == "Windows":
        directory = dir + "\\"
        directories = addMultipleDirectoryEndSeparators( dirs, 'Windows' )

    else:
        raise OSError( "Could not determine OS." )

    return directory, directories
