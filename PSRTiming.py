# Timing class, Python 3
# Henryk T. Haniewicz, 2018

# Local imports
from DataCulling import DataCull
from custom_exceptions import *

# Other imports
import os
from astropy.io import fits
import magic


# Timing class
class Timing:

    '''
    Class to deal with pulsar timing including calculating TOAs, putting them into
    TEMPO2 format, and creating fake TOAs for prediction models based on user defined criteria.
    '''

    def __init__( self, template, input, band, nsubint, jump = None, saveDirectory = None, toaFile = None ):

        '''
        Initializes an instance of the class with a required template and a directory or file to time
        as well as the frequency band as a string.
        Also requires an argument of the number of sub-integrations to average to before timing.
        '''

        # Initialize all parsed parameters as strings. Check for validity of nsubint (in case argparse doesn't)
        self.directory = str( input )

        # If a TOA save directory has been provided, initialize it. Otherwise, CWD.
        if saveDirectory is not None:
            self.saveDirectory = str( saveDirectory )
        else:
            self.saveDirectory = os.getcwd()

        if toaFile is not None:
            self.toaFile = str( toaFile )
        else:
            self.toaFile = "PSR_TOAs.toa"

        self.savePath = str( self.saveDirectory + self.toaFile )

        self.template = str( template )

        self.band = str( band )

        # Check if a post-TOA jump was provided
        if not jump:
            self.jump = None
        else:
            self.jump = str( jump )

        # Check if nsubint is an integer
        if not isinstance( nsubint, int ):
            raise TypeError( "nsubint argument must be an integer. Argument is currently {}".format( type( nsubint ).__name__ ) )
        elif nsubint <= 0:
            raise ValueError( "nsubint cannot be less than 1. Currently: {}".format( nsubint ) )

        self.nsubint = nsubint

        # Determine which version of getTOAs is needed (likely to change)
        if os.path.isdir( self.directory ):
            self.getTOAs_dir( save = self.savePath )
        elif os.path.isfile( self.directory ):
            self.getTOAs_file()
        else:
            raise OSError( "{} does not exist.".format( self.directory ) )



    def __repr__( self ):
        return "Timing( template = {}, file / directory = {}, frequencyBand = {}, nsubint = {}, jump = {} )".format( self.template, self.directory, self.band, self.nsubint, self.jump )

    def __str__( self ):
        return self.template, self.directory, self.band, self.subint, self.jump


    def getTOAs_dir( self, save = None, exciseRFI = False ):

        '''
        Calculate and return Time-of-Arrivals (TOAs) for the given directory.
        Each file can be chosen to undergo RFI excision before TOA calculation.
        '''

        # Cycle through each file in the stored directory
        for file in os.listdir( self.directory ):

            # Set the file to be a global variable in the class for use elsewhere
            self.file = file

            # Get the ASCII signature of the file header
            with magic.Magic() as m:
                format = m.id_filename( self.directory + self.file )

            # Check whether the file is a fits file using the header signature
            if format.find( "FITS image data, 8-bit, character or unsigned binary integer" ) == 0:

                # Check if the file is a calibration file and skip if it is
                if self.file.find( 'cal' ) == -1:

                    # Open the fits file header
                    try:
                        hdul = fits.open( self.directory + self.file )
                    except OSError:
                        print( "File {} did not match ASCII signature required for a fits file".format( self.file ) )
                        continue

                    # Get the frequency band used in the observation.
                    frontend = hdul[0].header[ 'FRONTEND' ]

                    # Close the header once it's been used or the program becomes very slow.
                    hdul.close()

                    # Create an object of the DataCull type
                    cullObject = DataCull( self.file, self.template, self.directory, printFull = False )

                    if cullObject.SNError:
                        continue

                    # If enabled, perform a standard RFI cull
                    if exciseRFI:
                        cullObject.reject( 'chauvenet', 15, True )

                    # Check if the band provided matches that in the header
                    if frontend == self.band:

                        # Scrunch factors. For TOAs, nchan should be 1 and nsubint is defined in class initialization
                        cullObject.ar.tscrunch( nsubint = self.nsubint )
                        cullObject.ar.fscrunch( nchan = 1 )

                        # Function to return the TOAs
                        cullObject.ar.time( cullObject.template, filename = save, MJD = True, jump = self.jump, header = False )


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

        # Temporary wizardry that requires explaination:
        # self.directory, as it's parsed in is actually the directory + file, so this splits everything up and re-assigns self.directory as the directory
        self.directory, self.file = os.path.split( self.directory )
        # But wait! self.directory above has no end "/" so we add one in
        self.directory = self.directory + "/"

        # Get the ASCII signature of the file header
        with magic.Magic() as m:
            format = m.id_filename( self.directory + self.file )

        # Check whether the file is a fits file using the header signature
        if format.find( "FITS image data, 8-bit, character or unsigned binary integer" ) == 0:

            # Check if the file is a calibration file (not included in the template)
            if self.file.find( 'cal' ) == -1:

                # Open the fits file header
                try:
                    hdul = fits.open( self.directory + self.file )
                except OSError:
                    print( "File {} did not match ASCII signature required for a fits file".format( self.file ) )
                    pass

                # Get the frequency band used in the observation.
                frontend = hdul[0].header[ 'FRONTEND' ]

                # Close the header once it's been used or the program becomes very slow.
                hdul.close()

                # Create an object of the DataCull type
                cullObject = DataCull( self.file, self.template, self.directory, printFull = False )

                if cullObject.SNError:
                    pass

                # If enabled, perform a standard RFI cull
                if exciseRFI:
                    cullObject.reject( 'chauvenet', 15, True )

                # Check if the band provided matches that in the header
                if frontend == self.band:

                    # Scrunch factors. For TOAs, nchan should be 1 and nsubint is defined in class initialization
                    cullObject.ar.tscrunch( nsubint = self.nsubint )
                    cullObject.ar.fscrunch( nchan = 1 )

                    # Function to return TOAs
                    cullObject.ar.time( cullObject.template, filename = self.savePath, MJD = True, jump = self.jump, header = False )


                else:
                    print( "Frontend provided for {} does not match frontend in fits file ( Input: {}, Expected: {} )".format( self.file, self.band, frontend ) )

            else:
                print( "Skipping calibration file..." )


        else:
            print( "{} is not a fits file...".format( self.file ) )
