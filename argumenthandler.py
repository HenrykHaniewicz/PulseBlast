# Command-line argument handler, Python 3
# Henryk T. Haniewicz, 2018

# Local imports
from PSRTiming import Timing
from custom_exceptions import *

# Other imports
import argparse
import os

class ArgumentHandler:

    def __init__( self, progname ):

        """
        Initializes the class using the program name as the argument.
        Initializes command line arguments and error checks.
        """

        # Initialize the program name
        self.progname = progname

        # Calls the  parser method in this class
        args = self.parser( progname )

        # Checks argument requirements for non-optional flags (as a double check)
        if ( not args.timingFlag ):
            raise ArgumentError( "Timing argument (-t / --time) required." )
        if ( not args.tempFlag ):
            raise ArgumentError( "Template argument (--temp) not initialized." )
        if ( not args.subintFlag ):
            raise ArgumentError( "Sub-integration argument (-s / --subint) required." )

        # Basically, if the jumpFlag isn't set, initialize it as a NoneType 1x1 array
        if args.jumpFlag is None:
            args.jumpFlag = [ None ]

        # textFile is optional. If no -f flag is provided, uses CWD
        if ( not args.textFile ):

             directory_in_str = str( os.getcwd() )

             for file in os.listdir( directory_in_str ):
                self.timing( file, args.timingFlag[0], args.tempFlag[0], args.subintFlag[0], args.jumpFlag[0], args.outputDirFlag, args.outputFlag )


        else:

            # If -f has been provided:
            for argument in args.textFile:

                    # Opens and separates the file into its lines
                    currentFile = open( argument, "r" )
                    loadedFile = currentFile.readlines()

                    # Read the lines in the file one by one
                    for line in loadedFile:

                        # Removes the 'new line' character introduced via readlines()
                        line = line.replace( "\n", "" )

                        # Calculates the TOAs
                        self.timing( line, args.timingFlag[0], args.tempFlag[0], args.subintFlag[0], args.jumpFlag[0], args.outputDirFlag, args.outputFlag )

                    currentFile.close()


    def __repr__( self ):
        return "ArgumentHandler( progname = {} )".format( self.progname )

    def __str__( self ):
        return self.progname



    def parser( self, progname ):

        """
        Initializes argparse and collects the command line arguments.
        Returns a list of input arguments.
        """

        # Initialize the parser
        parser = argparse.ArgumentParser( formatter_class = argparse.RawDescriptionHelpFormatter,
                    prog = progname,
                    description = '''\
                         PulseBlast Argument Handler
                    -------------------------------------
                       Argument handler for PulseBlast
                                 arguments.
                        ''' )

        # Arguments list
        parser.add_argument( '-x', '--file', dest = 'textFile', nargs = '*', default = None, help = 'Text file flag. Optional. Accepts as many txt files as necessary. Files can contain a mixture of directories and filenames.' )
        parser.add_argument( '-t', '--time', dest = 'timingFlag', nargs = 1, default = False, required = True, help = 'Timing flag. Required. Argument after flag takes the frequency band (to be improved).' )
        parser.add_argument( '--temp', dest = 'tempFlag', nargs = 1, required = True, help = 'Template flag. Required. Argument after flag takes the full path for the template profile.' )
        parser.add_argument( '-s', '--subint', dest = 'subintFlag', nargs = 1, type = int, required = True, help = 'Sub-integration scrunch flag. Required. Argument after flag takes an integer greater than 0.' )
        parser.add_argument( '-j', '--jump', dest = 'jumpFlag', nargs = '*', default = None, help = 'Jump flag. Optional. Argument takes a string that should correspond to a jump (or other) flag needed on the end of the TOAs.' )
        parser.add_argument( '-od', '--odir', dest = 'outputDirFlag', nargs = '?', default = None, help = 'TOA output directory. Optional. Argument takes a directory to save the TOA file to.' )
        parser.add_argument( '-o', '--output', dest = 'outputFlag', nargs = '?', default = None, help = 'TOA output filename. Optional. Argument takes the filename to save the TOAs to. Without, a default name is used.' )


        args = parser.parse_args()

        return args


    def timing( self, input, band, temp, nsubint, jump, saveDir, saveFile ):

        """
        Calls an instance of the Timing class.
        """

        timingObject = Timing( temp, input, band, nsubint, jump, saveDir, saveFile )
