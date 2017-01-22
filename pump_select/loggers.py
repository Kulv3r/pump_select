from __future__ import print_function
import os
import logging
from pprint import pprint


class FakeLogger(object):
    log_format = u'[{level}] {msg}'

    @staticmethod
    def _log(msg, level):
        print('- {} -'.format(level))
        pprint(msg)

    def debug(self, msg):
        self._log(msg, 'DEBUG')

    def info(self, msg):
        self._log(msg, 'INFO')

    def warning(self, msg):
        self._log(msg, 'WARNING')

    def error(self, msg):
        self._log(msg, 'ERROR')

    def critical(self, msg):
        self._log(msg, 'CRITICAL')


def get_logger():
    if os.environ.get('USER_PORTAL_ENV') == 'prod':
        return logging.getLogger('gunicorn.error')
    else:
        return FakeLogger()

logger = get_logger()
# logger.error('LOG ERROR MSG HERE')
# logger.info('LOG INFO MSG HERE')
# logger.debug('LOG DEBUG MSG HERE')
