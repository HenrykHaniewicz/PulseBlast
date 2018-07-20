# Timing class
# Henryk T. Haniewicz, 2018

# Local imports
from DataCulling import DataCull

# Other imports
import os
from astropy.io import fits
from custom_exceptions import *


# Timing class
class Timing:

    '''
    Class to deal with pulsar timing including calculating TOAs, putting them into
    TEMPO2 format, and creating fake TOAs for prediction models based on user defined criteria.
    '''

    def __init__( self, template, input, band, nsubint ):

        '''
        Initializes an instance of the class with a required template and a directory or file to time
        as well as the frequency band as a string.
        Also requires an argument of the number of sub-integrations to average to before timing.
        '''

        self.directory = str( input )

        self.template = str( template )

        self.band = str( band )

        if not isinstance( nsubint, int ):
            raise TypeError( "nsubint argument must be an integer. Argument is currently {}".format( type( nsubint ).__name__ ) )
        elif nsubint <= 0:
            raise ValueError( "nsubint cannot be less than 1. Currently: {}".format( nsubint ) )

        self.nsubint = nsubint

        if os.path.isdir( self.directory ):
            self.getTOAs_dir()
        elif os.path.isfile( self.directory ):
            self.getTOAs_file()
        else:
            raise OSError( "{} does not exist.".format( self.directory ) )



    def __repr__( self ):
        return "Timing( template = {}, file / directory = {}, frequencyBand = {}, nsubint = {} )".format( self.template, self.directory, self.band, self.nsubint )

    def __str__( self ):
        return self.template, self.directory, self.band, self.subint


    def getTOAs_dir( self, save = None, exciseRFI = False ):

        '''
        Calculate and return Time-of-Arrivals (TOAs) for the given directory.
        Each file can be chosen to undergo RFI excision before TOA calculation.
        '''

        # Cycle through each file in the stored directory
        for file in os.listdir( self.directory ):

            # Set the file to be a global variable in the class for use elsewhere
            self.file = file

            # Check whether the file is a fits file
            if self.file.endswith( ".fits" ) or self.file.endswith( ".refold" ):

                # Check if the file is a calibration file (not included in the template)
                if self.file.find( 'cal' ) == -1:

                    # Open the fits file header
                    hdul = fits.open( self.directory + self.file )

                    # Get the frequency band used in the observation.
                    frontend = hdul[0].header[ 'FRONTEND' ]

                    # Close the header once it's been used or the program becomes very slow.
                    hdul.close()

                    cullObject = DataCull( self.file, self.template, self.directory, printFull = False )

                    if cullObject.SNError:
                        continue

                    if exciseRFI:
                        cullObject.reject( 'chauvenet', 15, True )

                    # Check which band the fits file belongs to
                    if frontend == self.band:

                        cullObject.ar.tscrunch( nsubint = self.nsubint )
                        cullObject.ar.fscrunch( nchan = 1 )

                        cullObject.ar.time( cullObject.template, filename = save, MJD = True )


                    else:
                        print( "Frontend provided for {} does not match frontend in fits file ( Input: {}, Expected: {} )".format( self.file, self.band, frontend ) )

                else:
                    print( "Skipping calibration file..." )


            else:
                print( "{} is not a fits file...".format( self.file ) )


    def getTOAs_file( self, save = None, exciseRFI = False ):

        '''
        Calculate and return Time-of-Arrivals (TOAs) for the given file.
        Each file can be chosen to undergo RFI excision before TOA calculation.
        '''


        self.directory, self.file = os.path.split( self.directory )

        # Check whether the file is a fits file
        if self.file.endswith( ".fits" ) or self.file.endswith( ".refold" ):

            # Check if the file is a calibration file (not included in the template)
            if self.file.find( 'cal' ) == -1:

                # Open the fits file header
                hdul = fits.open( self.directory + "/" + self.file )

                # Get the frequency band used in the observation.
                frontend = hdul[0].header[ 'FRONTEND' ]

                # Close the header once it's been used or the program becomes very slow.
                hdul.close()

                cullObject = DataCull( self.file, self.template, self.directory + "/", printFull = False )

                if cullObject.SNError:
                    pass

                if exciseRFI:
                    cullObject.reject( 'chauvenet', 15, True )

                # Check which band the fits file belongs to
                if frontend == self.band:

                    cullObject.ar.tscrunch( nsubint = self.nsubint )
                    cullObject.ar.fscrunch( nchan = 1 )

                    cullObject.ar.time( cullObject.template, filename = save, MJD = True )


                else:
                    print( "Frontend provided for {} does not match frontend in fits file ( Input: {}, Expected: {} )".format( self.file, self.band, frontend ) )

            else:
                print( "Skipping calibration file..." )


        else:
            print( "{} is not a fits file...".format( self.file ) )
