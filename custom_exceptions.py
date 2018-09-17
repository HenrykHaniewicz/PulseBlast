# Custom exceptions file
# Add exceptions as necessary

class ArgumentError( Exception ):

    "Any place where incorrect or invalid arguments might exist should utilize this class."

    def __init__( self, message ):
        self.message = message
