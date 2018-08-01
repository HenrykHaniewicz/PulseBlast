# Pulsar Template class, Python 3
# Henryk T. Haniewicz, 2018

# PyPulse imports
from pypulse.archive import Archive

# Other imports
import os
import sys
import numpy as np
from astropy.io import fits
import magic


# Template class
class Template:

    '''
    Class for the creation, handling and analysis of pulsar template profiles.
    Templates are be created for one frequency band of data in a folder which can either be the current working directory or as many folders of the user's choosing.
    '''

    def __init__( self, band, *args ):

        '''
        Initializes the frequency band and the directories for use elsewhere in the class.
        '''

        # Here 'args' refers to a list of directories supplied by the user
        self.band = str( band )
        self.args = args

    def __repr__( self ):
        return "Template( frequency_band = {}, directories = {} )".format( self.band, self.args )

    def __str__( self ):
        return self.band, self.args


    def _loadArchive( self ):

        '''
        Loads the archive from the PyPulse Archive class and initializes the main parameters.
        '''

        loadedArchive = Archive( self.directory + self.file, verbose = False )

        return loadedArchive


    def _templateCreationScript( self ):

        '''
        Script to create a template.
        This should not be used in isolation but is accessed through the
        createTemplate method.
        '''

        # Load the archive
        archive = self._loadArchive()

        # Initialize the template if this is the first call
        if self._templateCreationScript.counter == 0:
            self.templateProfile = np.zeros( archive.getNbin(), dtype = float )
            self._templateCreationScript.__func__.counter += 1

        # Iterate through each subint and channel to add each profile together
        for time in np.arange( archive.getNsubint() ):
            for frequency in np.arange( archive.getNchan() ):
                self.templateProfile += archive.getData()[time][frequency]

        return self.templateProfile


    def createTemplate( self, filename = None, saveDirectory = None ):

        '''
        Loads the archive of each file in self.directory using PyPulse.
        Depending on the frequency band parsed at initialization, a template will be created for that frequency band, measuring it against the frontend in the fits file.
        Templates are saved in the saveDirectory as 1D numpy arrays with default extension .npy however any extension can be specified by the user.
        If arguments are not provided for the template name (without the .npy suffix) or directory name, a default file name and CWD will be used.
        '''

        print( "Beginning template creation..." )

        # Check if the filename has been provided
        if filename != None:

            # Initialize filename as a string
            filename_in_str = str( filename )

            # Split the filename up into a root and extension
            root, ext = os.path.splitext( filename_in_str )

            # If file extension does not exist, assume it is a .npy file
            if not ext:
                ext = '.npy'
                filename_in_str = root + ext

        # Set the templates to empty arrays
        self.templateProfile = []

        # Set the call counters for the creation scripts to 0
        self._templateCreationScript.__func__.counter = 0

        for i, arguments in enumerate( self.args ):

            # Check if the directory was supplied by the user. If not, use current working directory.
            if self.args == None:
                self.directory = str( os.getcwd() )
            else:
                self.directory = str( self.args[i] )

            if not os.path.isdir( self.args[i] ):
                raise NotADirectoryError( "{} is not a directory.".format( self.args[i] ) )

            # Cycle through each file in the stored directory
            for file in os.listdir( self.directory ):
                # Set the file to be a global variable in the class for use elsewhere
                self.file = str( file )

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
                        continue

                    # Check if the file is a calibration file and skip if it is
                    if hdul[0].header[ 'OBS_MODE' ] == 'PSR':

                        # Get the frequency band used in the observation.
                        try:
                            frontend = hdul[0].header[ 'FRONTEND' ]
                        except OSError:
                            print( "Could not find any frontend information in file {}".format( self.file ) )
                            continue

                        # Close the header once it's been used or the program becomes very slow.
                        hdul.close()

                        # Check which band the fits file belongs to
                        if frontend == self.band:

                            self.templateProfile = self._templateCreationScript()

                        else:
                            print( "Frontend provided for {} does not match frontend in fits file ( Input: {}, Expected: {} )".format( self.file, self.band, frontend ) )

                    elif hdul[0].header[ 'OBS_MODE' ] == 'CAL':
                        print( "Skipping calibration file..." )
                        hdul.close()

                    elif hdul[0].header[ 'OBS_MODE' ] == 'SEARCH':
                        print( "Skipping search file..." )
                        hdul.close()

                    else:
                        hdul.close()
                        raise OSError( "OBS_MODE found in file does not match known file types. ( Expected: PSR, CAL, SEARCH. Found: {} )".format( hdul[0].header[ 'OBS_MODE' ] ) )

                else:
                    print( "{} is not a fits file...".format( self.file ) )


            # Check if this is the last directory in the list
            if i == ( len( self.args ) - 1 ):

                # Check if a save name was provided and save as appropriate
                if filename == None and saveDirectory == None:
                    np.save( os.getcwd() + "Lbandtemplate.npy", self.templateProfile )
                elif filename == None:
                    np.save( saveDirectory + "Lbandtemplate.npy", self.templateProfile )
                else:
                    np.save( saveDirectory + filename_in_str, self.templateProfile )

        # Decide what to return based on doType
        print( "{} template profile created...".format( self.band ) )
        return self.templateProfile


    def deleteTemplate( self, dir, tempname ):

        '''
        Deletes a template file specified by the user (with both directory and filename as strings). If the template file parsed has no extension, the extension .npy will be searched for.
        Only use this if you know what you are doing as it is a delete function!
        '''

        # Parse the template's filename and directory into a string
        directory = str( dir + "/" )
        filename = str( tempname )

        # Ask user if they REALLY want to delete it
        if not input( "Are you sure you wish to delete {}{}? (y/n): ".format( directory, filename ) ).lower().strip()[:1] == "y": sys.exit(1)

        print( "Attempting to delete: {}{}".format( directory, filename ) )

        # Split the filename up into a root and extension
        root, ext = os.path.splitext( filename )

        # If file extension does not exist, assume it is a .npy file
        if not ext:
            ext = '.npy'
            filename = root + ext

        # if file exists, delete it. If not, raise FileNotFoundError
        if os.path.isfile( directory + filename ):
            os.remove( directory + filename )
            print( "{} deleted.".format( filename ) )
        else:
            raise FileNotFoundError( "Template file {} not found in {}".format( filename, directory ) )
