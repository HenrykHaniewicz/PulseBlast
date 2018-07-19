# Timing class
# Henryk T. Haniewicz, 2018


# Other imports
import os
from astropy.io import fits
from DataCulling import DataCull


# Timing class
class Timing:

    '''
    Class to deal with pulsar timing including calculating TOAs, putting them into
    TEMPO2 format, and creating fake TOAs based on user defined criteria.
    '''

    def __init__( self, template, input, band):

        '''
        Initializes an instance of the class with a required template and an
        optional directory for the template and files. If no directory is supplied,
        the CWD will be used.
        '''

        # Parse directory in string or choose CWD if no directory given

        self.directory = str( input )

        self.template = str( template )

        if os.path.isdir( self.directory ):
            self.getTOAs_dir( band )
        elif os.path.isfile( self.directory ):
            self.getTOAs_file( band )
        else:
            raise OSError( "File / directory does not exist." )



    def __repr__( self ):
        return "Timing( template = {}, directory = {} )".format( self.template, self.directory )

    def __str__( self ):
        return self.template, self.directory


    def getTOAs_dir( self, frequencyBand, save = None, exciseRFI = False ):

        '''
        Calculate and return Time-of-Arrivals (TOAs) for the given directory.
        Takes in a required argument for the frequency band (should match the template
        band loaded in initialization). Either 'L' or '430'.
        Each file can be chosen to undergo RFI excision before TOA calculation
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
                    if frequencyBand == 'L':

                        if frontend == 'lbw' or frontend == 'L_Band':

                            cullObject.ar.tscrunch( nsubint = 6 )
                            cullObject.ar.fscrunch( nchan = 1 )

                            cullObject.ar.time( cullObject.template, filename = save, MJD = True )

                        else:
                            print( "430 band file" )

                    elif frequencyBand == '430':

                        if frontend == '430':

                            cullObject.ar.tscrunch( nsubint = 2 )
                            cullObject.ar.fscrunch( nchan = 1 )

                            cullObject.ar.time( cullObject.template, filename = save, MJD = True )

                        else:
                            print( "L-Band file" )


                    else:
                        raise ValueError( "Frontend provided is neither 'L' nor '430'" )

                else:
                    print( "Skipping calibration file..." )


            else:
                print( "{} is not a fits file...".format( self.file ) )


    def getTOAs_file( self, frequencyBand, save = None, exciseRFI = False ):

        '''
        Calculate and return Time-of-Arrivals (TOAs) for the given directory.
        Takes in a required argument for the frequency band (should match the template
        band loaded in initialization). Either 'L' or '430'.
        Each file can be chosen to undergo RFI excision before TOA calculation
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
                if frequencyBand == 'L':

                    if frontend == 'lbw' or frontend == 'L_Band':

                        cullObject.ar.tscrunch( nsubint = 6 )
                        cullObject.ar.fscrunch( nchan = 1 )

                        cullObject.ar.time( cullObject.template, filename = save, MJD = True )

                    else:
                        print( "430 band file" )

                elif frequencyBand == '430':

                    if frontend == '430':

                        cullObject.ar.tscrunch( nsubint = 2 )
                        cullObject.ar.fscrunch( nchan = 1 )

                        cullObject.ar.time( cullObject.template, filename = save, MJD = True )

                    else:
                        print( "L-Band file" )


                else:
                    raise ArgumentError( "Frontend provided is neither 'L' nor '430'" )

            else:
                print( "Skipping calibration file..." )


        else:
            print( "{} is not a fits file...".format( self.file ) )


class ArgumentError( Exception ):

    def __init__( self, message ):
        self.message = message
