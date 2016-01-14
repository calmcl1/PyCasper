class CasparError(Exception):
    """Base class for Caspar Server exceptions.
    Where possible, the attribute 'command' will contain the AMCP string that raised the exception.
    """
    pass


class CommandNotUnderstoodError(CasparError):
    """Exception raised after a code 400 is returned by CCG.
    400 ERROR	- Command not understood
     """

    def __init__(self, command=None):
        self.cmd = command

    def __str__(self):
        return repr(self.cmd)


class IllegalVideoChannelError(CasparError):
    """Exception raised after a code 401 is returned by CCG.
    401 [command] ERROR - Illegal video_channel
     """

    def __init__(self, command=None):
        self.cmd = command

    def __str__(self):
        return repr(self.cmd)


class ParameterMissingError(CasparError):
    """Exception raised after a code 402 is returned by CCG.
    402 [command] ERROR - Parameter missing
     """

    def __init__(self, command=None):
        self.cmd = command

    def __str__(self):
        return repr(self.cmd)


class IllegalParameterError(CasparError):
    """Exception raised after a code 403 is returned by CCG.
    403 [command] ERROR - Illegal parameter
     """

    def __init__(self, command=None):
        self.cmd = command

    def __str__(self):
        return repr(self.cmd)


class MediaFileNotFoundError(CasparError):
    """Exception raised after a code 404 is returned by CCG.
    404 [command] ERROR - Media file not found
     """

    def __init__(self, command=None):
        self.cmd = command

    def __str__(self):
        return repr(self.cmd)


class InternalServerError(CasparError):
    """Exception raised after a code 500 is returned by CCG.
    500 FAILED - Internal server error
     """

    def __init__(self, command=None):
        self.cmd = command

    def __str__(self):
        return repr(self.cmd)


class MediaFileUnreadableError(CasparError):
    """Exception raised after a code 502 is returned by CCG.
    502 [command] FAILED - Media file unreadable
     """

    def __init__(self, command=None):
        self.cmd = command

    def __str__(self):
        return repr(self.cmd)
