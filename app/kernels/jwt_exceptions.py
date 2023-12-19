# -*- coding: utf-8 -*-

class DecodeException(Exception):
    """ This exception is used when the provided token is invalid and the function is not able to decode it. """

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.message = message


class TokenExpiredException(Exception):
    """ This exception is raised when the provided token is expired. """

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.message = message


class GenerationFailedException(Exception):
    """ This exception is raised when an error occurs while generating the JWT. """

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.message = message
