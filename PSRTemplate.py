# Pulsar Template class, Python 3
# Henryk T. Haniewicz, 2018

# Local imports
import otherUtilities as u

# PyPulse imports
from pypulse.archive import Archive

# Other imports
import os
import sys
import platform
import numpy as np
from astropy.io import fits
import magic

# Filter various annoying warnings (such as "cannot perform >= np.nan"). We know already...
import warnings
warnings.filterwarnings( "ignore" )


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


    def createTemplate( self, filename = None, saveDirectory = None, verbose = False ):

        '''
        Loads the archive of each file in self.directory using PyPulse.
        Depending on the frequency band parsed at initialization, a template will be created for that frequency band, measuring it against the frontend in the fits file.
        Templates are saved in the saveDirectory as 1D numpy arrays with default extension .npy however any extension can be specified by the user.
        If arguments are not provided for the template name (without the .npy suffix) or directory name, a default file name and CWD will be used.
        '''

        if verbose:
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
            if not self.args:
                self.directory = str( os.getcwd() )
            else:
                self.directory = str( self.args[i] )

            if not os.path.isdir( self.args[i] ):
                raise NotADirectoryError( "{} is not a directory.".format( self.args[i] ) )

            if not verbose:
                sys.stdout.write( '\n {0:<7s}  {1:<7s}\n'.format( 'Files', '% done' ) )

            # Cycle through each file in the stored directory
            for j, file in enumerate( os.listdir( self.directory ) ):
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
                        u.display_status( j, len( os.listdir( self.directory ) ) )
                        continue

                    # Check if the OBS_MODE is PSR and if not, skip it
                    if hdul[0].header[ 'OBS_MODE' ] == 'PSR':

                        # Get the frequency band used in the observation.
                        try:
                            frontend = hdul[0].header[ 'FRONTEND' ]
                        except OSError:
                            print( "Could not find any frontend information in file {}".format( self.file ) )
                            u.display_status( j, len( os.listdir( self.directory ) ) )
                            continue

                        # Close the header once it's been used or the program becomes very slow.
                        hdul.close()

                        # Check which band the fits file belongs to
                        if frontend == self.band:

                            self.templateProfile = self._templateCreationScript()

                        else:
                            if verbose:
                                print( "Frontend provided for {} does not match frontend in fits file ( Input: {}, Expected: {} )".format( self.file, self.band, frontend ) )
                            else:
                                u.display_status( j, len( os.listdir( self.directory ) ) )
                                continue

                    # Potential custom handling when OBS_MODE is CAL or SEARCH
                    elif hdul[0].header[ 'OBS_MODE' ] == 'CAL':
                        if verbose:
                            print( "Skipping calibration file..." )
                        hdul.close()

                    elif hdul[0].header[ 'OBS_MODE' ] == 'SEARCH':
                        if verbose:
                            print( "Skipping search file..." )
                        hdul.close()

                    # If none of the options are present, raise OSError
                    else:
                        hdul.close()
                        raise OSError( "OBS_MODE found in file does not match known file types. ( Expected: PSR, CAL, SEARCH. Found: {} )".format( hdul[0].header[ 'OBS_MODE' ] ) )

                # If the binary signature doesn't match that of a fits file, skip completely
                else:
                    if verbose:
                        print( "{} is not a fits file...".format( self.file ) )
                    else:
                        u.display_status( j, len( os.listdir( self.directory ) ) )
                        continue

                u.display_status( j, len( os.listdir( self.directory ) ) )


            # Check if this is the last directory in the list
            if i == ( len( self.args ) - 1 ):

                # Check if a save name was provided and save as appropriate
                if filename == None and saveDirectory == None:
                    np.save( os.getcwd() + "PSR_template.npy", self.templateProfile )
                elif filename == None:
                    np.save( saveDirectory + "PSR_template.npy", self.templateProfile )
                else:
                    np.save( saveDirectory + filename_in_str, self.templateProfile )

        # Decide what to return based on doType
        if verbose:
            print( "{} template profile created...".format( self.band ) )
        else:
            print( "Done" )
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

        filename = u.addExtension( filename, 'npy' )

        # if file exists, delete it. If not, raise FileNotFoundError
        if os.path.isfile( directory + filename ):
            os.remove( directory + filename )
            print( "{} deleted.".format( filename ) )
        else:
            raise FileNotFoundError( "Template file {} not found in {}".format( filename, directory ) )


# Basically an argument handler and program executer if this file is run in the terminal
if __name__ == "__main__":

    from custom_exceptions import ArgumentError
    import argparse

    # Default attempt to find the gooey package but switch to argparse if not
    try:
        from gooey import Gooey, GooeyParser
        GUI = True
    except ImportError:
        GUI = False


    # Define a different main function with and without the gooey decorator
    if GUI:
        @Gooey( terminal_panel_color = '#000000', terminal_font_color = '#FFFFFF' )
        def main():

            parser = GooeyParser( prog = 'PSRTemplate.py',
                            description = '''\
                               PulseBlast Template Argument Handler
                           -------------------------------------------
                            Argument handler for PulseBlast Templates
                                ''' )


            # Arguments list
            parser.add_argument( '-b', dest = 'band', metavar = 'Frequency Band', nargs = 1, default = None, help = 'Frequency band of observation. This should match the band string in the PSRFITS file.' )
            parser.add_argument( '-o', dest = 'outputfile', metavar = 'Output File', nargs = 1, default = None, widget = 'FileSaver', help = 'Name of the output file and path (select). Standard extention is .npy but any other extension can overwrite this.' )
            parser.add_argument( '-d', dest = 'directories', metavar = 'Directories List', nargs = '*', default = None, widget = 'MultiDirChooser', help = 'Directories to search for PSRFITS files in. Directories should be seperated by a space' )

            args = parser.parse_args()

            # Checks argument requirements for non-optional flags (as a double check)
            if ( not args.band ):
                raise ArgumentError( "Frequency band argument required." )
            if ( not args.outputfile ):
                raise ArgumentError( "Output file name argument required." )
            if ( not args.directories ):
                raise ArgumentError( "At least one directory argument is required." )

            # Formats the directories based on OS
            directories = u.formatMultipleDirectories( args.directories )

            # Makes sure directories and files are all in the right format for parsing in any OS
            odir, ofile = os.path.split( args.outputfile[0] )
            odir, idirs = u.addDirectoryEndSeparators( odir, directories )

            # Initialize the template class object as normal and run the template creation script
            templateObject = Template( args.band[0], *idirs )
            templateObject.createTemplate( ofile, odir )

    # If the UI package is unavailable
    else:
        def main():

            parser = argparse.ArgumentParser( formatter_class = argparse.RawDescriptionHelpFormatter,
                            prog = 'PSRTemplate.py', description = '''\
                               PulseBlast Template Argument Handler
                           -------------------------------------------
                            Argument handler for PulseBlast Templates
                                ''' )

            parser.add_argument( '-b', dest = 'band', metavar = 'Frequency Band', nargs = 1, default = None, help = 'Frequency band of observation. This should match the band string in the PSRFITS file.' )
            parser.add_argument( '-o', dest = 'outputfile', metavar = 'Output File', nargs = 1, default = None, help = 'Name of the output file and path. Standard extention is .npy but any other extension can overwrite this.' )
            parser.add_argument( '-d', dest = 'directories', metavar = 'Directories List', nargs = '*', default = None, help = 'Directories to search for PSRFITS files in. Directories should be seperated by a space' )

            args = parser.parse_args()


            # Checks argument requirements for non-optional flags (as a double check)
            if ( not args.band ):
                raise ArgumentError( "Frequency band argument required." )
            if ( not args.outputfile ):
                raise ArgumentError( "Output file name argument required." )
            if ( not args.directories ):
                raise ArgumentError( "At least one directory argument is required." )


            # Makes sure directories and files are all in the right format for parsing in any OS
            odir, ofile = os.path.split( args.outputfile[0] )
            odir, idirs = u.addDirectoryEndSeparators( odir, args.directories )


            # Initialize the template class object as normal and run the template creation script
            templateObject = Template( args.band[0], *idirs )
            templateObject.createTemplate( ofile, odir )


    # Run the main function
    main()
