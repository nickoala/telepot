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

class TelegramError(TelepotException):
    def __init__(self, description, error_code):
        super(TelegramError, self).__init__(description, error_code)

    @property
    def description(self):
        return self.args[0]

    @property
    def error_code(self):
        return self.args[1]

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
