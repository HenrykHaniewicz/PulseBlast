# Re-structure

# PulseBlast imports
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

        self.progname = progname

        args = self.parser( progname )

        if ( not args.timingFlag ):
            raise ArgumentError( "Timing argument (-t / --time) required." )
        if ( not args.tempFlag ):
            raise ArgumentError( "Template argument (--temp) not initialized." )

        if ( not args.textFile ):

             directory_in_str = str( os.getcwd() )

             for file in os.listdir( directory_in_str ):
                self.timing( file, args.timingFlag[0], args.tempFlag[0] )


        else:

            for argument in args.textFile:

                    currentFile = open( argument, "r" )

                    loadedFile = currentFile.readlines()

                    for line in loadedFile:

                        line = line.replace( "\n", "" )

                        self.timing( line, args.timingFlag[0], args.tempFlag[0] )

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

        parser = argparse.ArgumentParser( formatter_class = argparse.RawDescriptionHelpFormatter,
                    prog = progname,
                    description = '''\
                         PulseBlast Argument Handler
                    -------------------------------------
                       Argument handler for PulseBlast
                                 arguments.
                        ''' )

        parser.add_argument( '-f', '--file', dest = 'textFile', nargs = '*', default = None, help = 'Text file flag. Optional. Accepts as many txt files as necessary. Files can contain a mixture of directories and filenames.' )
        parser.add_argument( '-t', '--time', dest = 'timingFlag', nargs = 1, default = False, help = 'Timing flag. Required. Argument after flag takes the frequency band (to be improved).' )
        parser.add_argument( '--temp', dest = 'tempFlag', nargs = 1, help = 'Template flag. Required. Argument after flag takes the full path for the template profile.' )

        args = parser.parse_args()

        return args


    def timing( self, input, band, temp ):

        """
        Calls an instance of the Timing class.
        """

        timingObject = Timing( temp, input, band )
