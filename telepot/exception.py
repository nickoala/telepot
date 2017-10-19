import sys

class TelepotException(Exception):
    """ Base class of following exceptions. """
    pass

class BadFlavor(TelepotException):
    def __init__(self, offender):
        super(BadFlavor, self).__init__(offender)

    @property
    def offender(self):
        return self.args[0]

PY_3 = sys.version_info.major >= 3

class BadHTTPResponse(TelepotException):
    """
    All requests to Bot API should result in a JSON response. If non-JSON, this
    exception is raised. While it is hard to pinpoint exactly when this might happen,
    the following situations have been observed to give rise to it:

    - an unreasonable token, e.g. ``abc``, ``123``, anything that does not even
      remotely resemble a correct token.
    - a bad gateway, e.g. when Telegram servers are down.
    """

    def __init__(self, status, text, response):
        super(BadHTTPResponse, self).__init__(status, text, response)

    @property
    def status(self):
        return self.args[0]

    @property
    def text(self):
        return self.args[1]

    @property
    def response(self):
        return self.args[2]

class EventNotFound(TelepotException):
    def __init__(self, event):
        super(EventNotFound, self).__init__(event)

    @property
    def event(self):
        return self.args[0]

class WaitTooLong(TelepotException):
    def __init__(self, seconds):
        super(WaitTooLong, self).__init__(seconds)

    @property
    def seconds(self):
        return self.args[0]

class IdleTerminate(WaitTooLong):
    pass

class StopListening(TelepotException):
    pass

class TelegramError(TelepotException):
    """
    To indicate erroneous situations, Telegram returns a JSON object containing
    an *error code* and a *description*. This will cause a ``TelegramError`` to
    be raised. Before raising a generic ``TelegramError``, telepot looks for
    a more specific subclass that "matches" the error. If such a class exists,
    an exception of that specific subclass is raised. This allows you to either
    catch specific errors or to cast a wide net (by a catch-all ``TelegramError``).
    This also allows you to incorporate custom ``TelegramError`` easily.

    Subclasses must define a class variable ``DESCRIPTION_PATTERNS`` which is a list
    of regular expressions. If an error's *description* matches any of the regular expressions,
    an exception of that subclass is raised.
    """

    def __init__(self, description, error_code, json):
        super(TelegramError, self).__init__(description, error_code, json)

    @property
    def description(self):
        return self.args[0]

    @property
    def error_code(self):
        return self.args[1]

    @property
    def json(self):
        return self.args[2]

class UnauthorizedError(TelegramError):
    DESCRIPTION_PATTERNS = ['unauthorized']

class BotWasKickedError(TelegramError):
    DESCRIPTION_PATTERNS = ['bot.*kicked']

class BotWasBlockedError(TelegramError):
    DESCRIPTION_PATTERNS = ['bot.*blocked']

class TooManyRequestsError(TelegramError):
    DESCRIPTION_PATTERNS = ['too *many *requests']

class MigratedToSupergroupChatError(TelegramError):
    DESCRIPTION_PATTERNS = ['migrated.*supergroup *chat']

class NotEnoughRightsError(TelegramError):
    DESCRIPTION_PATTERNS = ['not *enough *rights']
