# Custom exceptions file.
# Add exceptions as necessary

class ArgumentError( Exception ):

    def __init__( self, message ):
        self.message = message
