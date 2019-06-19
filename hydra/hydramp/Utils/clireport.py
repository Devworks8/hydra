import logging

# TODO: Finish implementing logging


class CLIReport:
    def __init__(self, settings=None):
        self.settings = settings
        self.logger = logging.getLogger()
        self.handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def report(self, level=None, message=''):
        if level is None:
            print(self.report('WARNING', 'Missing report level.'))

        elif level == 'INFO':
            print('{level}: {message}'.format(level=level, message=message))

        elif level == 'WARNING':
            print('{level}: {message}'.format(level=level, message=message))

        elif level == 'ERROR':
            print('{level}: {message}'.format(level=level, message=message))

        else:
            print(self.report('WARNING'))
