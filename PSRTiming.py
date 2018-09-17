# Timing class, Python 3
# Henryk T. Haniewicz, 2018

# Local imports
from DataCulling import DataCull
from custom_exceptions import *
import otherUtilities as u

# Other imports
import os
import sys
from astropy.io import fits
import magic


# Timing class
class Timing:

    '''
    Class to deal with pulsar timing including calculating TOAs, putting them into
    TEMPO2 format, and creating fake TOAs for prediction models based on user defined criteria.
    '''

    def __init__( self, template, input, band, nsubint, jump = None, saveDirectory = None, toaFile = None, verbose = False, RFI = None ):

        '''
        Initializes an instance of the class with a required template and a directory or file (collectively known as 'input') to time
        as well as the frequency band as a string, number of time sub-integrations to scrunch to, user defined strings (jump) at the end of
        the TOAs, a directory to save the timing file to and the filename of that file. The jump and save locations are optional. If no save
        directory is parsed, CWD will be used. Finally, one can set the verbose and RFI excision flags.
        '''

        # Initialize all parsed parameters as strings. Check for validity of nsubint (in case argparse doesn't)
        self.directory = str( input )

        self.verbose = verbose

        self.rfi = RFI

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
            self.jump = ""
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
            self.getTOAs_dir( save = self.savePath, exciseRFI = RFI )
        elif os.path.isfile( self.directory ):
            self.getTOAs_file( exciseRFI = RFI )
        else:
            raise OSError( "{} does not exist.".format( self.directory ) )



    def __repr__( self ):
        return "Timing( template = {}, file / directory = {}, frequencyBand = {}, nsubint = {}, jump = {}, saveDirectory = {}, toaFile = {}, verbose = {}, RFI = {} )".format( self.template, self.directory, self.band, self.nsubint, self.jump, self.saveDirectory. self.toaFile, self.verbose, self.rfi )

    def __str__( self ):
        return self.template, self.directory, self.band, self.subint, self.jump, self.saveDirectory, self.toaFile, self.verbose, self.rfi


    def getTOAs_dir( self, save = None, exciseRFI = None ):

        '''
        Calculate and return Times-of-Arrival (TOAs) for the given directory.
        Each file can be chosen to undergo RFI excision before TOA calculation.
        '''

        if not self.verbose:
            sys.stdout.write( '\n {0:<7s}  {1:<7s}\n'.format( 'Files', '% done' ) )

        # Cycle through each file in the stored directory
        for i, file in enumerate( os.listdir( self.directory ) ):

            # Set the file to be a global variable in the class for use elsewhere
            self.file = file

            # Get the ASCII signature of the file header
            with magic.Magic() as m:
                format = m.id_filename( self.directory + self.file )

            # Check whether the file is a fits file using the header signature
            if format.find( "FITS image data, 8-bit, character or unsigned binary integer" ) == 0:

                # Open the fits file header
                try:
                    hdul = fits.open( self.directory + self.file )
                except OSError:
                    print( "File {} did not match ASCII signature required for a fits file".format( self.file ) )
                    u.display_status( i, len( os.listdir( self.directory ) ) )
                    continue

                # Check if the OBS_MODE is PSR and if not, skip it
                if hdul[0].header[ 'OBS_MODE' ] == 'PSR':

                    # Get the frequency band used in the observation.
                    try:
                        frontend = hdul[0].header[ 'FRONTEND' ]
                    except OSError:
                        print( "Could not find any frontend information in file {}".format( self.file ) )
                        u.display_status( i, len( os.listdir( self.directory ) ) )
                        continue

                    # Close the header once it's been used or the program becomes very slow.
                    hdul.close()

                    # Create an object of the DataCull type
                    cullObject = DataCull( self.file, self.template, self.directory, verbose = self.verbose )

                    if cullObject.SNError:
                        continue

                    # If enabled, perform a standard RFI cull
                    if exciseRFI is not None and isinstance( exciseRFI, int ):
                        cullObject.reject( 'chauvenet', self.rfi, self.verbose )

                    # Check if the band provided matches that in the header
                    if frontend == self.band:

                        # Scrunch factors. For TOAs, nchan should be 1 and nsubint is defined in class initialization
                        cullObject.ar.tscrunch( nsubint = self.nsubint )
                        cullObject.ar.fscrunch( nchan = 1 )

                        # Function to return the TOAs
                        cullObject.ar.time( cullObject.template, filename = save, MJD = True, flags = self.jump, appendto = True )


                    else:
                        if self.verbose:
                            print( "Frontend provided for {} does not match frontend in fits file ( Input: {}, Expected: {} )".format( self.file, self.band, frontend ) )
                        else:
                            u.display_status( i, len( os.listdir( self.directory ) ) )
                            continue

                # Potential custom handling when OBS_MODE is CAL or SEARCH
                elif hdul[0].header[ 'OBS_MODE' ] == 'CAL':
                    if self.verbose:
                        print( "Skipping calibration file..." )
                    hdul.close()

                elif hdul[0].header[ 'OBS_MODE' ] == 'SEARCH':
                    if self.verbose:
                        print( "Skipping search file..." )
                    hdul.close()

                # If none of the options are present, raise OSError
                else:
                    hdul.close()
                    raise OSError( "OBS_MODE found in file does not match known file types. ( Expected: PSR, CAL, SEARCH. Found: {} )".format( hdul[0].header[ 'OBS_MODE' ] ) )

            # If the binary signature doesn't match that of a fits file, skip completely
            else:
                if self.verbose:
                    print( "{} is not a fits file...".format( self.file ) )
                else:
                    u.display_status( i, len( os.listdir( self.directory ) ) )
                    continue

            u.display_status( i, len( os.listdir( self.directory ) ) )


    def getTOAs_file( self, save = None, exciseRFI = None ):

        '''
        Calculate and return Times-of-Arrivals (TOAs) for the given file.
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

            # Open the fits file header
            try:
                hdul = fits.open( self.directory + self.file )
            except OSError:
                print( "File {} did not match ASCII signature required for a fits file".format( self.file ) )
                pass

            # Check if the OBS_MODE is PSR and if not, skip it
            if hdul[0].header[ 'OBS_MODE' ] == 'PSR':

                # Get the frequency band used in the observation.
                try:
                    frontend = hdul[0].header[ 'FRONTEND' ]
                except OSError:
                    print( "Could not find any frontend information in file {}".format( self.file ) )
                    pass

                # Close the header once it's been used or the program becomes very slow.
                hdul.close()

                # Create an object of the DataCull type
                cullObject = DataCull( self.file, self.template, self.directory, verbose = self.verbose )

                if cullObject.SNError:
                    pass

                # If enabled, perform a standard RFI cull
                if exciseRFI is not None and isinstance( exciseRFI, int ):
                    cullObject.reject( 'chauvenet', self.rfi, self.verbose )

                # Check if the band provided matches that in the header
                if frontend == self.band:

                    # Scrunch factors. For TOAs, nchan should be 1 and nsubint is defined in class initialization
                    cullObject.ar.tscrunch( nsubint = self.nsubint )
                    cullObject.ar.fscrunch( nchan = 1 )

                    # Function to return TOAs
                    cullObject.ar.time( cullObject.template, filename = self.savePath, MJD = True, flags = self.jump, appendto = True )


                else:
                    if self.verbose:
                        print( "Frontend provided for {} does not match frontend in fits file ( Input: {}, Expected: {} )".format( self.file, self.band, frontend ) )
                    else:
                        pass

            # Potential custom handling when OBS_MODE is CAL or SEARCH
            elif hdul[0].header[ 'OBS_MODE' ] == 'CAL':
                if self.verbose:
                    print( "Skipping calibration file..." )
                hdul.close()

            elif hdul[0].header[ 'OBS_MODE' ] == 'SEARCH':
                if self.verbose:
                    print( "Skipping search file..." )
                hdul.close()

            # If none of the options are present, raise OSError
            else:
                hdul.close()
                raise OSError( "OBS_MODE found in file does not match known file types. ( Expected: PSR, CAL, SEARCH. Found: {} )".format( hdul[0].header[ 'OBS_MODE' ] ) )

        # If the binary signature doesn't match that of a fits file, skip completely
        else:
            if self.verbose:
                print( "{} is not a fits file...".format( self.file ) )
            else:
                pass
