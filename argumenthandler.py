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

        # textFile is optional. If no -f flag is provided, uses CWD
        if ( not args.textFile ):

             directory_in_str = str( os.getcwd() )

             for file in os.listdir( directory_in_str ):
                self.timing( file, args.timingFlag[0], args.tempFlag[0], args.subintFlag[0] )


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
                        self.timing( line, args.timingFlag[0], args.tempFlag[0], args.subintFlag[0] )

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
        parser.add_argument( '-f', '--file', dest = 'textFile', nargs = '*', default = None, help = 'Text file flag. Optional. Accepts as many txt files as necessary. Files can contain a mixture of directories and filenames.' )
        parser.add_argument( '-t', '--time', dest = 'timingFlag', nargs = 1, default = False, help = 'Timing flag. Required. Argument after flag takes the frequency band (to be improved).' )
        parser.add_argument( '--temp', dest = 'tempFlag', nargs = 1, help = 'Template flag. Required. Argument after flag takes the full path for the template profile.' )
        parser.add_argument( '-s', '--subint', dest = 'subintFlag', nargs = 1, type = int, help = 'Sub-integration scrunch flag. Required. Argument after flag takes an integer greater than 0.' )

        args = parser.parse_args()

        return args


    def timing( self, input, band, temp, nsubint ):

        """
        Calls an instance of the Timing class.
        """

        timingObject = Timing( temp, input, band, nsubint )
