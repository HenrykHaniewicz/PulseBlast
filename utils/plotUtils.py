# Plotting utilities

# Imports
import random
import numpy as np
import matplotlib.pyplot as plt

color_list = [ 'b', 'g', 'r', 'c', 'y', 'm' ]


def histogram_and_curves( array, mean = 0.0, stdDev = 1.0, bins = None, xAxis = 'X', yAxis = 'Y', zAxis = 'Z', show = True, *curves ):

    """
    Plots a histogram of a data array in 1 or 2 dimensions.
    """

    color = 'k'
    bgcolor = 'w'
    style = 'bar'

    fig = plt.figure( figsize = (6,6) )
    ax = fig.add_subplot( 111, facecolor = bgcolor )

    if bins is None:
        bins = np.arange( np.amin( array ), np.amax( array ) )

    XMIN = mean - ( 4 * stdDev )
    XMAX = mean + ( 4 * stdDev )

    ax.set_xlim( XMIN, XMAX )
    ax.set_ylim( 0, 1 )
    t = np.arange( XMIN , XMAX, 0.01)

    if array.ndim is 1:

        # Plot the 1D histogram
        n, bins, patches = ax.hist( array, bins = bins, density = True, color = color, histtype = style )

        ax.plot( t, spyst.norm.pdf(t), color = random.choice( color_list ) )
        ax.plot( t, spyst.vonmises.pdf(t, 1), color = random.choice( color_list ) )

        # Plot distribution curves
        #if curves:
        #    for curve in curves:
        #        ax.plot( t, curve, color = random.choice( dashed_color_list ) )
                #ax.plot( t, curve, color = 'r' )

        if show:
            plt.show()

    elif array.ndim is 2:
        raise ValueError()

    else:
        print( "Invalid dimensions. Required: 1 or 2. (Actual: {})".format( array.ndim ) )

    return ax


def waterfall( array, ax = None, offset = None, border = 0, labels = True, bins = None, show = True ):

    """
    Waterfall plot of an array. Requires an array of 2 dimensions.
    """

    if array.ndim is 2:
        if offset is None:
            offset = np.max( np.average( array, axis = 0 ) )

        fig = plt.figure( figsize = (6,6) )
        bgcolor = 'w'
        ax = fig.add_subplot( 111, facecolor = bgcolor )
        color = 'k'

        if bins is None:
            bins = np.arange( array.shape[1] )


        XMIN = 0
        XMAX = len( bins ) - 1
        YMIN = 0 - offset
        YMAX = ( 1 + len( array ) ) * offset
        XLOW = XMIN - ( XMAX - XMIN ) * border
        XHIGH = ( XMAX - XMIN ) * border + XMAX
        YLOW = YMIN - ( YMAX - YMIN ) * border
        YHIGH = ( YMAX - YMIN ) * border + YMAX


        for i in np.arange( len( array ) ):
            ax.plot( array[i][bins] + offset * i, color )

        ax.set_xlim( XLOW, XHIGH )
        ax.set_ylim( YLOW, YHIGH )

        if not labels:
            ax.set_xticklabels([])
            ax.set_yticklabels([])
        if show:
            plt.show()
    else:
        print( "Invalid dimensions. Required: 2. (Actual: {})".format( array.ndim ) )

    return ax


def greyscale( array, ax = None, cbar = False, mask = None, show = True, filename = None, setnan = 0.0, **kwargs ):

    """Basic imshow of array"""

    if array.ndim is 2:
        if mask is not None:
            imshow( np.ma.masked_array( array, mask = mask ), ax = ax, **kwargs )
        else:
            imshow( array, ax = ax, **kwargs )
        if cbar:
            plt.colorbar()
        if filename is not None:
            plt.savefig( filename )
        if show:
            plt.show()
        else:
            plt.close()
    else:
        print( "Invalid dimensions. Required: 2. (Actual: {})".format( array.ndim ) )
    return ax

def imshow( x, ax = None, origin = 'lower', interpolation = 'nearest', aspect = 'auto', **kwargs ):
    if ax is not None:
        im = ax.imshow( x, origin = origin, interpolation = interpolation, aspect = aspect, **kwargs )
    else:
        im = plt.imshow( x, origin = origin, interpolation = interpolation, aspect = aspect, **kwargs )
    return im



if __name__ == "__main__":

    import scipy.stats as spyst
    import scipy.optimize as opt

    array = np.random.vonmises( mu = 0, kappa = 1, size = 64 )

    print(array)

    histogram_and_curves( array )
