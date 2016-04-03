class TelepotException(Exception):
    pass

class BadFlavor(TelepotException):
    def __init__(self, offender):
        super(BadFlavor, self).__init__(offender)

    @property
    def offender(self):
        return self.args[0]

class BadHTTPResponse(TelepotException):
    def __init__(self, status, text):
        super(BadHTTPResponse, self).__init__(status, text)

    @property
    def status(self):
        return self.args[0]

    @property
    def text(self):
        return self.args[1]

    def __unicode__(self):
        return 'Status %d - First 500 characters are shown below:\n%s' % (self.status, self.text[:500])
        
    def __str__(self):
        return unicode(self).encode('utf-8')


class TelegramError(TelepotException):
    def __init__(self, description, error_code):
        super(TelegramError, self).__init__(description, error_code)

    @property
    def description(self):
        return self.args[0]

    @property
    def error_code(self):
        return self.args[1]

class UnauthorizedError(TelegramError):
    DESCRIPTION_PATTERNS = ['unauthorized']

class BotWasKickedError(TelegramError):
    DESCRIPTION_PATTERNS = ['bot.*kicked']

class BotWasBlockedError(TelegramError):
    DESCRIPTION_PATTERNS = ['bot.*blocked']


class WaitTooLong(TelepotException):
    pass

class StopListening(TelepotException):
    def __init__(self, code=None, reason=None):
        super(StopListening, self).__init__(code, reason)

    @property
    def code(self):
        return self.args[0]

    @property
    def reason(self):
        return self.args[1]
