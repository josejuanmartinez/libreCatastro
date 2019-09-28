#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config
import sys
from logging.handlers import RotatingFileHandler

from src.settings import config


class CadastroLogger:
    """Custom logger for keeping track of the libreCatastro Scrapping"""

    def __init__(self, class_name):
        """Constructor"""

        '''default root console logging'''
        self.logger = logging.getLogger(class_name)
        self.logger.setLevel(logging.DEBUG)

        '''console file logging'''
        debug_file_handler = logging.StreamHandler(sys.stdout)
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.addFilter(
            type('', (logging.Filter,), {'filter': staticmethod(lambda r: r.levelno <= logging.DEBUG)}))

        '''error file logging'''
        error_file_handler = RotatingFileHandler(config['error_log_file'], mode='a', maxBytes=5 * 1024 * 1024,
                                         backupCount=100, encoding='utf-8', delay=0)

        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.addFilter(type('', (logging.Filter,), {'filter': staticmethod(lambda r: r.levelno <= logging.ERROR)}))

        '''tracking file logging'''
        tracking_file_handler = RotatingFileHandler(config['tracking_log_file'], mode='a', maxBytes=5 * 1024 * 1024,
                                           backupCount=100, encoding='utf-8', delay=0)

        tracking_file_handler.setLevel(logging.INFO)
        tracking_file_handler.addFilter(
            type('', (logging.Filter,), {'filter': staticmethod(lambda r: r.levelno <= logging.INFO)}))

        self.logger.addHandler(debug_file_handler)
        self.logger.addHandler(error_file_handler)
        self.logger.addHandler(tracking_file_handler)

