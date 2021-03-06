_loggers = {}

def getLogger(name):
    if not name in _loggers:
        _loggers[name] = Logger()
    return _loggers[name]

class Logger:

    def __init__(self):
        self.events = []

    def info(self, msg, object=None):
        e = Event(msg, "INFO", object)
        self.events.append(e)

    def warning(self, msg, object=None):
        e = Event(msg, "WARNING", object)
        self.events.append(e)

    def error(self, msg, object=None):
        e = Event(msg, "ERROR", object)
        self.events.append(e)

    def critical(self, msg, object=None):
        e = Event(msg, "CRITICAL", object)
        self.events.append(e)

    def flush(self):
        self.events = []

    def is_empty(self):
        return len(self.events) == 0

    def get_events(self, levels="INFO WARNING ERROR CRITICAL"):
        """
        get_events("ERROR CRITICAL")
        possible levels: INFO, WARNING, ERROR, CRITICAL
        """

        result = []
        for l in levels.split():
            result += filter(lambda e: e.level == l, self.events)
        return sorted(result, key=lambda e: e.line_number)

    def has(self, level):
        """
        Check if there are events of specified levels.
        possible levels: INFO, WARNING, ERROR, CRITICAL
        has("ERROR CRITICAL")
        """

        return len(self.get_events(level)) > 0

class Event:

    def __init__(self, msg, level, object):
        self.msg = msg
        self.level = level
        self.line_number = 0

        if object is not None:
            self.object = object.name
            if object.code_object is not None:
                self.line_number = object.code_object.position + 1

    def __str__(self):
        value = self.level
        if self.line_number is not None:
            value += ":" + str(self.line_number)
        elif self.object is not None:
            value += " " + self.object.name
        value += ": " + self.msg
        return value
