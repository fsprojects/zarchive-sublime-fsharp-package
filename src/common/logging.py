from datetime import datetime


DEBUG = 0
INFO = 10
WARNING = 20
ERROR = 30
CRITICAL = 40


class LoggerBase(object):

    LABEL_INFO = 'INFO'
    LABEL_WARNING = 'WARNING'
    LABEL_ERROR = 'ERROR'
    LABEL_DEBUG = 'DEBUG'
    LABEL_CRITICAL = 'CRITICAL'

    def __init__(self, origin=''):
        self.origin = origin
        self._level = DEBUG

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value

    def log(self, label, message, *args):
        message = message % args
        time_stamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self.emit("[{}] {} - {}".format(label, time_stamp, message))

    def info(self, message, *args):
        if not self.check_should_log(INFO):
            return
        message = str(message) % args
        self.log(LoggerBase.LABEL_INFO, message)

    def warn(self, message, *args):
        if not self.check_should_log(WARNING):
            return
        message = str(message) % args
        self.log(LoggerBase.LABEL_WARNING, message)

    def error(self, message, *args):
        if not self.check_should_log(ERROR):
            return
        message = str(message) % args
        self.log(LoggerBase.LABEL_ERROR, message)

    def critical(self, message, *args):
        if not self.check_should_log(CRITICAL):
            return
        message = str(message) % args
        self.log(LoggerBase.LABEL_CRITICAL, message)

    def debug(self, message, *args):
        if not self.check_should_log(DEBUG):
            return
        message = str(message) % args
        self.log(LoggerBase.LABEL_DEBUG, message)

    def check_should_log(self, level):
        return level >= self.level

    def emit(self, message):
        raise NotImplementedError()


class NullLogger(LoggerBase):

    def emit(self, message):
        pass
