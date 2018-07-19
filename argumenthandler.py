# Re-structure

# PulseBlast imports
from PSRTiming import Timing
from PSRTiming import ArgumentError

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
        parser = argparse.ArgumentParser(
             prog = progname,
             description = 'Test' )

        parser.add_argument( '-f', '--file', dest = 'textFile', nargs = '*', default = None, help = 'Test' )
        parser.add_argument( '-t', '--time', dest = 'timingFlag', nargs = 1, default = False, help = 'Test2' )
        parser.add_argument( '--temp', dest = 'tempFlag', nargs = 1, help = 'Test3' )

        args = parser.parse_args()

        return args


    def timing( self, input, band, temp ):

        """
        Calls an instance of the Timing class.
        """

        timingObject = Timing( temp, input, band )
