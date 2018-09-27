# Utilities for pulsar calculations (code by Robert Ferdman)

# Imports
import numpy as np
import math
import utils.otherUtilities as u
import utils.mathUtils as mu

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

# Returns the mean and RMS of the off-pulse window
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


# Returns the profile data minus the baseline
def removeBase( profData, duty ):

     baseline, baseRMS = getBase( profData, duty )

     # remove baseline mean from profile in place
     profData = profData - baseline

     return profData


# Contour things

def loadContourArrays( fileprefix ):

    """
    Loads a numpy array of a set filename structure
    """

    load_array = np.load(fileprefix+'_params.npy')
    # for the purposes of this routine, only need the following
    # things in p_out
    p_out = {'m2':load_array[0],
             'mtot':load_array[1],
             'm1':load_array[2],
             'm1_prob':load_array[3]}
    p_out['norm_like'] = np.load(fileprefix+'_prob.npy')

    return p_out


# def plot_contour_pdf(x_val, y_val, contour_data, n_steps=32,\
#                          norm=False, weights=None, \
#                          canvassize=None, xticks=True, yticks=True, \
#                          xlabel=True, ylabel=True, linecolour='black', \
#                          xlim=None, ylim=None, figtext=None, figtextsize=16, \
#                          hgrid=False, vgrid=False,
#                          ticklabelsize=18, axislabelsize=18):

def plot_contour_pdf( x_val, y_val, contour_data, n_steps = 64, linecolour = 'black', **kwargs ):

    u.check_kwarg( None, 'weights', 'canvassize', 'xlim', 'ylim', 'figtext', **kwargs )
    u.check_kwarg( True, 'xticks', 'yticks', 'xlabel', 'ylabel', **kwargs )
    u.check_kwarg( False, 'norm', 'hgrid', 'vgrid', **kwargs )
    u.check_kwarg( 16, 'figtextsize', **kwargs )
    u.check_kwarg( 18, 'ticklabelsize', 'axislabelsize', **kwargs )
    u.check_kwarg( 35, 'xstart', 'xend', 'ystart', 'yend', **kwargs )


# If weights are None, assign them to ones, with the same shape as the
# input z array:
    if weights is None:
        weights = np.ones_like( contour_data, dtype = float )
# If weights are given, ensure they are the same shape as z:
    else:
        if weights.shape is not contour_data.shape:
            print( 'Shape of weight array ', weights.shape, ' does not match the input data array ', contour_data.shape )
            return None

# Start by setting up lot limits.  Assuming 1-D array input:
    xmin = np.min( x_val )
    xmax = np.max( x_val )
    ymin = np.min( y_val )
    ymax = np.max( y_val )
    xspan = abs( xmax - xmin )
    yspan = abs( ymax - ymin )

# Set up the plot:
    fig = plt.figure( figsize = canvassize )
    ax = fig.add_axes( [xstart, ystart, xend, yend] )
    ax.xaxis.set_tick_params( labelsize = ticklabelsize, pad = 8 )
    ax.yaxis.set_tick_params( labelsize = ticklabelsize, pad = 8 )
    ax.ticklabel_format( axis = 'x', useOffset = False )
    ax.ticklabel_format( axis = 'y', useOffset = False )
    if xlim is None:
        ax.set_xlim( xmin - 0.01*xspan, xmax + 0.02*xspan )
    else:
        ax.set_xlim( xlim )
    if ylim is None:
        ax.set_ylim( ymin - 0.01*yspan, ymax + 0.02*yspan )
    else:
        ax.set_ylim( ylim )

    if xlabel is not None:
        ax.set_xlabel( xlabel, fontsize = axislabelsize, labelpad = 12 )
    if ylabel is not None:
        ax.set_ylabel( ylabel, fontsize = axislabelsize, labelpad = 12 )

    if not xticks:
        for tick in ax.xaxis.get_major_ticks():
            tick.label1On = False
            tick.label2On = False

    if not yticks:
        for tick in ax.yaxis.get_major_ticks():
            tick.label1On = False
            tick.label2On = False

    if hgrid:
        ax.yaxis.grid(linestyle = '--', color = 'black', linewidth = 0.4 )
    if vgrid:
        ax.xaxis.grid( linestyle = '--', color = 'black', linewidth = 0.4 )

    prob_intervals = np.array( [0.683, 0.954, 0.9973] )

# Create levels at which to plot contours at each of the above intervals.
# Will not assume going in that Z values are normalized to total volume of 1.
    contour_level = get_prob_2D_levels( contour_data, prob_intervals, n_steps = n_steps )
    print( "CONTOUR_LEVEL = ", contour_level )

    if norm is True:
        z_val = ( contour_data*weights ) / np.sum( contour_data*weights )
    else:
        z_val = contour_data

# Now plot the pdf data
    ax.contour( x_val, y_val, z_val, levels = np.flip( contour_level, axis = 0 ), colors = ( 'red', 'blue', 'green' ) )

    if figtext is not None:
        for txt in figtext:
            ax.text( txt[0], txt[1], txt[2], fontsize = figtextsize, horizontalalignment = 'center', verticalalignment = 'center' )



def get_prob_2D_levels( z, prob_intervals, norm = False, n_steps = 64, weights = None ):

    
