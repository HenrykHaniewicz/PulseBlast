# Extra utilities

# Imports
import sys
import os
import platform
import numpy as np
import matplotlib.pyplot as plt


def zeroWeights( criterion = None, archive = None, verbose = False ):

    '''
    Scans through each sub-integration and channel and sets any bad scans to zero.
    '''

    if criterion is None:
        raise ValueError( "Please provide a rejection criterion" )
    elif archive is None:
        raise ValueError( "Please provide an archive" )

    for time, frequency in zip( np.where( criterion )[0], np.where( criterion )[1] ):
        if verbose:
            print( "Setting the weight of (subint: {}, channel: {}) to 0".format( time, frequency ) )
        archive.setWeights( 0, t = time, f = frequency )


def getRMSArrayProperties( array, mask ):

    '''
    Returns the RMS array, a linearized RMS array, the mean and standard deviation
    '''

    # Return the array of RMS values for each profile
    r = mathu.rmsMatrix2D( array, mask = mask, nanmask = True )

    # Reshape RMS array to be linear and store in a new RMS array
    l = np.reshape( r, ( array.shape[0] * array.shape[1] ) )

    # Mean and standard deviation
    m, s = np.nanmean( l ), np.nanstd( l )

    return r, l, m, s

# Delete and flush the current line on the console
def restart_line():
     sys.stdout.write( '\r' )
     sys.stdout.flush()

# Simple progress bar
def display_status( iteration, MAX_ITER ):
    restart_line()

    sys.stdout.write('{0:<10d}[{1:>3d}%]'.format( iteration, int( 100 * float( iteration )/float( MAX_ITER ) ) ) )
    sys.stdout.flush()

# (conv function) Plots and shows a vector and maybe a curve or two using matplotlib then frees up memory
def plotAndShow( vector, *curves ):
    plt.plot( vector )
    if curves:
        for curve in curves:
            plt.plot( curve, color = 'r--' )
    plt.show()
    plt.close()


def addExtension( file, ext, save = False, overwrite = False ):

    '''
    Add any desired extension to a file that doesn't have one.
    If the file does, that extension will be used instead unless overwrite is
    checked.
    '''

    if not isinstance( ext, str ):
        raise TypeError( "Extension must be a string" )

    # Split the filename up into a root and extension
    root, end = os.path.splitext( file )

    # If file extension does not exist, add the extension
    if (not end) or overwrite:
        end = '.' + ext
        fileout = root + end
    else:
        fileout = file

    # Rename the file in os if enabled
    if save:
        os.rename( file, fileout )

    return fileout


# Formats directories from GUI output to console. Need to test on Windows...
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

# Adds the correct separator (based on platform) to the end of the directories parsed.
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


def check_kwarg( action, *args, **kwargs ):

    for argument in args:

        if not argument in kwargs:
            keyword == action
