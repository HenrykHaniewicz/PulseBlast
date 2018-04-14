# Data Culling Class, Python 3
# Henryk T. Haniewicz, 2018

# PyPulse imports
from pypulse.archive import Archive
from pypulse.singlepulse import SinglePulse
from pypulse.utils import get_toa3

# Plotting imports
import matplotlib.pyplot as plt
import scipy.stats as spyst

# Other imports
import numpy as np
import math
import choice
import os
import mathUtils
import otherUtilities as utils

# Filter various annoying warnings (such as "cannot perform >= np.nan"). We know already...
import warnings
warnings.filterwarnings( "ignore" )


# Data culling class
class DataCull:

    '''
    Main class for data culling pulsar fits files to get a less noisy data set.
    Calling the class itself simply takes an optional directory and a filename.
    If no directory is given, the current working directory will be used.
    '''

    def __init__( self, filename, directory = None, SNLim = 3000, printFull = False ):

        '''
        Initializes all archives and parameters in the data cube for a given file.
        A custom signal / noise lower bound can also be set on initialization but
        the default is 3000.
        This will exit the current archive if the signal / noise ratio is lower
        than the threshold.
        One can also set whether long arrays are to be printed in full or in
        shorthand.
        '''

        print( "Initializing DataCull object..." )

        # Parse directory in string or choose CWD if no directory given
        if directory == None:
            self.directory = str( os.getcwd() )
        else:
            self.directory = str( directory )

        # Parse filename
        if os.path.isfile( self.directory + filename ):
            self.filename = str( filename )
        else:
            print( "Error: File {} not found in this directory...".format( filename ) )
            exit()

        # Parse printFull option
        self.printFull = printFull

        # Parse SNLim
        self.SNLim = SNLim

        # Load the file in the archive
        self.ar = Archive( self.__str__(), verbose = False )

        # Togglable print options
        if printFull == True:
            np.set_printoptions( threshold = np.nan )

        # Check if Signal / Noise is too low
        if self.ar.getSN() < SNLim:
            print( "Signal / Noise ratio is way too low. (Below {})".format( SNLim ) )
            print( "Data set to be thrown out..." )
            exit()

        # Load the data cube for the file
        self.data = self.ar.getData()

        # Initialize data skewness to be overwritten later
        self.skewness = 0.0

        print( "Archive loaded for {}...".format( self.filename ) )


    def __repr__( self ):
        return "DataCull( filename = {}, directory = {}, SNLim = {}, printFull = {} )".format( self.filename, self.directory, self.SNLim, self.printFull )

    def __str__( self ):
        return self.directory + self.filename


    def loadTemplate( self, templateFilename ):

        '''
        Loads a template specified by the user. If no extension is given, the
        extension .npy will be used. Note that this code is designed for numpy
        arrays so it would be wise to use them.
        Returns the template.
        '''

        # Parse the template's filename into a string
        templateFilename = str( templateFilename )
        root, ext = os.path.splitext( templateFilename )

        # If file extension does not exist, assume it is a .npy file
        if not ext:
            ext = '.npy'
            templateFilename = root + ext

        # Load the template
        template = np.load( self.directory + templateFilename )

        print( "Template {} loaded...".format( templateFilename ) )

        return template


    def rmsRejection( self, template, criterion, showPlot = False ):

        '''
        Rejects outlier root mean squared values for off pulse regions and
        re-weights the data cube in the loaded archive.
        '''

        # Re-load the data cube for the file
        self.data = self.ar.getData()

        # Return the array of RMS values for each profile
        rmsArray = self.createRmsMatrix( template )

        # Reshape RMS array to be linear and store in a new RMS array
        linearRmsArray = np.reshape( rmsArray, ( self.ar.getNchan() * self.ar.getNsubint() ) )

        # Best fit of data using a Gaussian fit
        mu, sigma = np.nanmean( linearRmsArray ), np.nanstd( linearRmsArray )

        if showPlot == True:

            # Creates the histogram
            self.histogramPlot( linearRmsArray, mu, sigma, 0, 'Root Mean Squared', 'Frequency Density' )

            plt.show()

        # Determine which criterion to use to reject data
        if criterion == 'chauvenet': # Chauvenet's Criterion

            rejectionCriterion = mathUtils.chauvenet( rmsArray, mu, sigma )

        elif criterion == 'DMAD': # Double Median Absolute Deviation

            rejectionCriterion = mathUtils.doubleMAD( linearRmsArray )
            rejectionCriterion = np.reshape( rejectionCriterion, ( self.ar.getNsubint(), self.ar.getNchan() ) )

        else:
            print( "Allowed rejection criteria are either 'chauvenet' or 'DMAD'. Please use one of these..." )
            exit()

        # Set the weights of potential noise in each profile to 0
        for time, frequency in zip( np.where( rejectionCriterion )[0], np.where( rejectionCriterion )[1] ):
            print( "Setting the weight of (subint: {}, channel: {}) to 0".format( time, frequency ) )
            self.ar.setWeights( 0, t = time, f = frequency )

        # Checks to see if there were any data to reject. If this array has length 0, all data was good and the completion flag is set to true.
        if( len( np.where( rejectionCriterion )[0] ) == 0 ):
            self.rejectionCompletionFlag = True

        print( "Data rejection cycle complete..." )


    def reject( self, template, criterion = 'chauvenet', iterations = 1 ):

        '''
        Performs the rejection algorithm until the number of iterations has been
        reached or the data culling is complete, whichever comes first. The
        default number of iterations is 1.
        Requires a template and criterion to be set with the default criterion
        being Chauvenet's criterion.
        This is the function you should use to reject all outliers fully.
        '''

        # Kurtosis (skewness)

        print( "Beginning data rejection for {}...".format( self.filename ) )

        # Initialize the completion flag to false
        self.rejectionCompletionFlag = False

        for i in np.arange( iterations ):

            self.rmsRejection( template, criterion, False )

            # If all possible outliers have been found and the flag is set to true, don't bother doing any more iterations.
            if self.rejectionCompletionFlag == True:
                generation = i + 1
                print( "RMS data rejection for {} complete after {} generations...".format( self.filename, generation ) )
                break

        # If the completion flag is still false, the cycles finished before full excision
        if self.rejectionCompletionFlag == False:
            print( "Maximum number of iterations ({}) completed...".format( iterations ) )

        # Re-initialize the completion flag to false
        self.rejectionCompletionFlag = False

        for i in np.arange( iterations ):

            self.binShiftRejection( template, False )

            # If all possible outliers have been found and the flag is set to true, don't bother doing any more iterations.
            if self.rejectionCompletionFlag == True:
                generation = i + 1
                print( "Bin shift data rejection for {} complete after {} generations...".format( self.filename, generation ) )
                break

        # If the completion flag is still false, the cycles finished before full excision
        if self.rejectionCompletionFlag == False:
            print( "Maximum number of iterations ({}) completed...".format( iterations ) )


        # Re-load the data cube for the file
        self.data = self.ar.getData()


    def createRmsMatrix( self, template ):

        '''
        Creates an array of RMS values for each profile in one file.
        '''

        # Initialize RMS table of zeros
        rmsMatrix = np.zeros( ( self.ar.getNsubint(), self.ar.getNchan() ), dtype = float )

        # Create a mask along the bin space on the template profile
        mask = utils.binMaskFromTemplate( template )

        # Loop over the time and frequency indices (subints and channels)
        for time in np.arange( self.ar.getNsubint() ):
            for frequency in np.arange( self.ar.getNchan() ):

                # Calculate the RMS of the off-pulse region and assign it to the relevant index
                rmsMatrix[time][frequency] = mathUtils.rootMeanSquare( self.data[time][frequency][mask == 0] )

                if all( amp == 0 for amp in self.data[time][frequency] ):
                    rmsMatrix[time][frequency] = np.nan

        # Mask the nan values in the array so that histogramPlot doesn't malfunction
        rmsMatrix = np.ma.array( rmsMatrix, mask = np.isnan( rmsMatrix ) )

        print( "Root Mean Square matrix successfully created..." )

        # Returns the masked RMS matrix
        return rmsMatrix


    def binShiftRejection( self, template, showPlot = False ):

        '''
        Gets the bin shift and bin shift errors of each profile in the file and
        plots both quantities as a histogram.
        Then, rejects based on Chauvenet criterion
        '''

        nBinShift, nBinError = self.getBinShifts( template )

        # Reshape the bin shift and bin shift error arrays to be linear
        linearNBinShift, linearNBinError = np.reshape( nBinShift, ( self.ar.getNchan() * self.ar.getNsubint() ) ), np.reshape( nBinError, ( self.ar.getNchan() * self.ar.getNsubint() ) )

        # Mean and standard deviation of the bin shift
        muS, sigmaS = np.nanmean( linearNBinShift ), np.nanstd( linearNBinShift )

        # Mean and standard deviation of the bin shift error
        muE, sigmaE = np.nanmean( linearNBinError ), np.nanstd( linearNBinError )

        if showPlot == True:

            # Create the histograms as two subplots
            plt.subplot(211)
            self.histogramPlot( linearNBinShift, muS, sigmaS, 0, r'Bin Shift from Template, $\hat{\tau}$', 'Frequency Density' )
            plt.subplot(212)
            self.histogramPlot( linearNBinError, muE, sigmaE, 1, r'Bin Shift Error, $\sigma_{\tau}$', 'Frequency Density' )

            # Adjust subplots so they look nice
            plt.subplots_adjust( top=0.92, bottom=0.15, left=0.15, right=0.95, hspace=0.55, wspace=0.40 )

            plt.show()

        rejectionCriterionS, rejectionCriterionE = mathUtils.chauvenet( nBinShift, muS, sigmaS ), mathUtils.chauvenet( nBinError, muE, sigmaE )

        # Set the weights of potential noise in each profile to 0
        for time, frequency in zip( np.where( rejectionCriterionS )[0], np.where( rejectionCriterionS )[1] ):
            print( "Setting the weight of (subint: {}, channel: {}) to 0".format( time, frequency ) )
            self.ar.setWeights( 0, t = time, f = frequency )

        for time, frequency in zip( np.where( rejectionCriterionE )[0], np.where( rejectionCriterionE )[1] ):
            print( "Setting the weight of (subint: {}, channel: {}) to 0".format( time, frequency ) )
            self.ar.setWeights( 0, t = time, f = frequency )

        # Checks to see if there were any data to reject. If this array has length 0, all data was good and the completion flag is set to true.
        if len( np.where( rejectionCriterionS )[0] ) and len( np.where( rejectionCriterionE )[0] ) == 0:
            self.rejectionCompletionFlag = True

        print( "Data rejection cycle complete..." )

    def getBinShifts( self, template ):

        '''
        Returns the bin shift and bin shift error.
        '''

        print( "Getting bin shifts and errors from the template..." )

        # Re-load the data cube
        self.data = self.ar.getData()

        # Return the array of RMS values for each profile
        rmsArray = self.createRmsMatrix( template )

        # Initialize the bin shifts and bin shift errors
        nBinShift = np.zeros( ( self.ar.getNsubint(), self.ar.getNchan() ), dtype = float )
        nBinError = np.zeros( ( self.ar.getNsubint(), self.ar.getNchan() ), dtype = float )

        # Use PyPulse utility get_toa3 to obtain tauhat and sigma_tau for each profile and feed them into the two arrays.
        for time in np.arange( self.ar.getNsubint() ):
            for frequency in np.arange( self.ar.getNchan() ):

                if all( amp == 0 for amp in self.data[time][frequency] ):

                    nBinShift[time][frequency] = np.nan
                    nBinError[time][frequency] = np.nan

                else:

                    # Attempt to calculate the bin shift and error. If not possible, set the profile to 0.
                    try:
                        tauccf, tauhat, bhat, sigma_tau, sigma_b, snr, rho = get_toa3( template, self.data[time][frequency], rmsArray[time][frequency], dphi_in=0.1, snrthresh=0., nlagsfit=5, norder=2 )

                        nBinShift[time][frequency] = tauhat
                        nBinError[time][frequency] = sigma_tau

                    except:
                        print( "Setting the weight of (subint: {}, channel: {}) to 0".format( time, frequency ) )
                        self.ar.setWeights( 0, t = time, f = frequency )

                        nBinShift[time][frequency] = np.nan
                        nBinError[time][frequency] = np.nan

        # Mask the nan values in the array so that histogramPlot doesn't malfunction
        nBinShift, nBinError = np.ma.array( nBinShift, mask = np.isnan( nBinShift ) ), np.ma.array( nBinError, mask = np.isnan( nBinError ) )

        return nBinShift, nBinError


    def histogramPlot( self, array, mean = 0, stdDev = 1, fit = 0, xAxis = 'x-axis', yAxis = 'y-axis' ):

        '''
        Plots and returns a histogram of some linear data array using matplotlib
        and fits either a Gaussian (fit = 0), half-Gaussian (fit = 1) or skewnorm (fit = 2)
        centered around the mean with a spread of stdDev.
        If no mean or stddev are provided, a fit centered around a mean of 0 with
        stddev of 1 will be used. If a fit is given outside the range, Gaussian is used.
        Also use this function to set the x and y axis names.
        '''

        # Plot the histogram
        n, bins, patches = plt.hist( array, bins = self.ar.getNchan(), density = True, color = 'black' )

        # Add a 'best fit' probability distribution function based on the fit parameter
        if fit == 0 or fit > 2:
            xPlot = np.linspace( ( mean - ( 4 * stdDev ) ), ( mean + ( 4 * stdDev ) ), 1000 )
            yPlot = spyst.norm.pdf( xPlot, mean, stdDev )
        elif fit == 1:
            xPlot = np.linspace( 0, ( mean + ( 4 * stdDev ) ), 1000 )
            yPlot = spyst.halfnorm.pdf( xPlot, mean, stdDev )
        else:
            xPlot = np.linspace( ( mean - ( 4 * stdDev ) ), ( mean + ( 4 * stdDev ) ), 1000 )
            yPlot = spyst.skewnorm.pdf( xPlot, self.skewness, mean, stdDev )

        l = plt.plot( xPlot, yPlot, 'r--', linewidth = 2 )

        # Format axes. If matplotlibrc has been modified to allow LaTeX, plots will use LaTeX
        plt.ylabel( yAxis )
        plt.xlabel( xAxis )
        plt.title( r'$\mu=%.3f,\ \sigma=%.3f$' % ( mean, stdDev ) )
        plt.grid( True )

        # Returns a 3-tuple of the form data, frequency bins, patches
        return n, bins, patches


    def waterfallPlot( self, offset ):

        '''
        Plots pulse profiles as a waterfall plot using PyPulse.
        If the data cube is of incorrect shape to parse to PyPulse, the user is
        asked to scrunch the data along as many axes as necessary.
        Alternatively, the user can quit the function / program entirely.
        '''

        if len( np.shape( self.ar.getData() ) ) == 2:
            self.ar.waterfall( offset = offset, border = 0.1 )

        elif len( np.shape( self.ar.getData() ) ) > 2:
            print( "Please perform enough dimensional scrunches to reduce the dimensions to 2." )
            print( "Perform a full scrunch in one dimension?" )
            choice = self.scrunchChoices()
            if choice != 'exit':
                self.waterfallPlot( offset )

        else:
            print( "Too few dimensions. Please check the data set or retry." )

        return self


    def greyscalePlot( self ):

        '''
        Plots pulse profiles as a greyscale plot using PyPulse.
        If the data cube is of incorrect shape to parse to PyPulse, the user is
        asked to scrunch the data along as many axes as necessary.
        Alternatively, the user can quit the function / program entirely.
        '''

        if len( np.shape( self.ar.getData() ) ) == 2:
            plt.xlabel( "Phase bins" )
            self.ar.imshow( cbar = True )

        elif len( np.shape( self.ar.getData() ) ) > 2:
            print( "Please perform enough dimensional scrunches to reduce the dimensions to 2." )
            print( "Perform a full scrunch in one dimension?" )
            choice = self.scrunchChoices()
            if choice != 'exit':
                self.greyscalePlot()

        else:
            print( "Too few dimensions. Please check the data set or retry." )

        return self


    def scrunchChoices( self ):

        '''
        Allows the user to make a selection on which dimension they would like
        to scrunch in.
        '''

        # Choose from a set of options
        scrunchChoice = choice.Menu( ['time', 'frequency', 'polarization', 'exit'] ).ask()
        if scrunchChoice == 'time':
            self.ar.tscrunch()
        elif scrunchChoice == 'frequency':
            self.ar.fscrunch( nchan = 1 )
        elif scrunchChoice == 'polarization':
            self.ar.pscrunch()
        else:
            print( "Exiting choices..." )

        return scrunchChoice
