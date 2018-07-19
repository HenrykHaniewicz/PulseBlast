# Pulsar Template Class, Python 3
# Henryk T. Haniewicz, 2018

# System imports
import os

# PyPulse imports
from pypulse.archive import Archive

# Other imports
import numpy as np
from astropy.io import fits


# Template class
class Template:

    '''
    Class for the creation, handling and analysis of pulsar template profiles.
    Templates can be created for each frequency band of data in a folder which
    can either be the current working directory or a folder of the user's
    choosing.
    '''

    def __init__( self, *args ):

        self.args = args

    def __repr__( self ):
        return "Template( directories = {} )".format( self.args )

    def __str__( self ):
        return self.args


    def _loadArchive( self ):

        '''
        Loads the archive from the PyPulse Archive class and initializes the main parameters.
        '''

        loadedArchive = Archive( self.directory + self.file, verbose = False )

        return loadedArchive


    def _templateCreationScriptL( self ):

        '''
        Script to create a template of all files in the L-band.
        This should not be used in isolation but is accessed through the
        createTemplate method.
        '''

        # Load the archive
        archive = self._loadArchive()

        # Initialize the template if this is the first call
        if self._templateCreationScriptL.counter == 0:
            self.templateProfileL = np.zeros( archive.getNbin(), dtype = float )
            self._templateCreationScriptL.__func__.counter += 1

        # Iterate through each subint and channel to add each profile together
        for time in np.arange( archive.getNsubint() ):
            for frequency in np.arange( archive.getNchan() ):
                self.templateProfileL += archive.getData()[time][frequency]

        return self.templateProfileL


    def _templateCreationScript430( self ):

        '''
        Script to create a template of all files in the 430-band.
        This should not be used in isolation but is accessed through the
        createTemplate method.
        '''

        # Load the archive
        archive = self._loadArchive()

        # Initialize the template if this is the first call
        if self._templateCreationScript430.counter == 0:
            self.templateProfile430 = np.zeros( archive.getNbin(), dtype = float )
            self._templateCreationScript430.__func__.counter += 1

        # Iterate through each subint and channel to add each profile together
        for time in np.arange( archive.getNsubint() ):
            for frequency in np.arange( archive.getNchan() ):
                self.templateProfile430 += archive.getData()[time][frequency]

        return self.templateProfile430


    def createTemplate( self, doType = 0, bandNameL = None, bandName430 = None ):

        '''
        Loads the archive of each file in the directory using PyPulse.
        Depending on the choice made on initialization, a template will be
        created for one band (of the user's choosing) or all bands.
        Templates are saved in self.directory (either CWD or whatever the user
        wishes) as 1D numpy arrays, .npy. If arguments are not provided for the
        template names (without the .npy suffix), default names will be used.

        Useage of the doType parameter: 0 (default) does both bands and returns a tuple.
        1 does only the L-band.
        2 does only the 430-band.
        '''

        print( "Beginning template creation..." )

        # Initialize the file names if given
        nameL = str( bandNameL ) + ".npy"
        name430 = str( bandName430 ) + ".npy"

        # Set the templates to empty arrays
        self.templateProfile430, self.templateProfileL = [], []

        # Set the call counters for the creation scripts to 0
        self._templateCreationScript430.__func__.counter = 0
        self._templateCreationScriptL.__func__.counter = 0

        for i, arguments in enumerate( self.args ):

            # Check if the directory was supplied by the user. If not, use current working directory.
            if self.args == None:
                self.directory = str( os.getcwd() )
            else:
                self.directory = str( self.args[i] )

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
                        frequencyBand = hdul[0].header[ 'FRONTEND' ]

                        # Close the header once it's been used or the program becomes very slow.
                        hdul.close()

                        # Check which band the fits file belongs to
                        if frequencyBand == 'lbw' or frequencyBand == 'L_Band':

                            if doType == 0 or doType == 1:
                                self.templateProfileL = self._templateCreationScriptL()

                                if i == ( len( self.args ) - 1 ):

                                    # Check if a save name was provided
                                    if bandNameL == None:
                                        np.save( self.directory + "Lbandtemplate.npy", self.templateProfileL )
                                    else:
                                        np.save( self.directory + nameL, self.templateProfileL )
                            else:
                                print( "L-Band file" )

                        elif frequencyBand == '430':

                            if doType == 0 or doType == 2:
                                self.templateProfile430 = self._templateCreationScript430()

                                if i == ( len( self.args ) - 1 ):

                                    # Check if a save name was provided
                                    if bandName430 == None:
                                        np.save( self.directory + "430bandtemplate.npy", self.templateProfile430 )
                                    else:
                                        np.save( self.directory + name430, self.templateProfile430 )
                            else:
                                print( "430-Band file" )

                        else:
                            print( "Frontend is neither L-Band, nor 430-Band..." )

                    else:
                        print( "Skipping calibration file..." )


                else:
                    print( "{} is not a fits file...".format( self.file ) )

        # Decide what to return based on doType
        if doType == 0:
            print( "Template profiles created..." )
            return self.templateProfileL, self.templateProfile430
        elif doType == 1:
            print( "L-Band template profile created..." )
            return self.templateProfileL
        else:
            print( "430-Band template profile created..." )
            return self.templateProfile430


    def deleteTemplate( self, name ):

        '''
        Deletes a template file name specified by the user. If the template file
        parsed has no extension, the extension .npy will be searched for.
        Only use this if you know what you are doing as it is a delete function!
        '''

        # Parse the template's filename into a string
        filename = str( name )
        print( "Attempting to delete: {}...".format( filename ) )

        # Split the filename up into a root and extension
        root, ext = os.path.splitext( filename )

        # If file extension does not exist, assume it is a .npy file
        if not ext:
            ext = '.npy'
            filename = root + ext

        # if file exists, delete it
        if os.path.isfile( self.directory + filename ):
            os.remove( self.directory + filename )
            print( "{} deleted.".format( filename ) )
        else:
            print( "Error: Template file {} not found".format( filename ) )
