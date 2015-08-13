
#!/usr/bin/python

__author__ = 'macOzone'

import sys
import threading
from datetime import datetime


class Logger(object):
    def __init__(self, filename="Default.log"):
        self._bReady = False
        self._locker = threading.Lock()
        self._terminal = sys.stdout
        try:
            self._logger = open(filename, 'wb')
            self._bReady = True
        except:
            pass

    def log(self, message):
        if self._bReady:
            with self._locker:
                message += '\n'
                self._logger.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'--> '+message)

    def write(self, message):
        if self._bReady:
            with self._locker:
                message += '\n'
                self._terminal.write(message)
                self._logger.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'--> '+message)

    def __del__(self):
        if self._bReady:
            self._logger.close()
