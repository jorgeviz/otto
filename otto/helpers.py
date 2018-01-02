# -*- coding: utf-8 -*-
import logging
import sys

class ottoHelpers(object):
    """ Class to manage all needed dependecy objects for otto
    """

    def __init__(self):
        """ Constructor
        """
        self.start_logger()

    def start_logger(self):
        """ Method to start Otto logger
        """
        # Logger just Works for Python3, this will be updated 
        self.logger = logging.getLogger('Otto-CT-v0.0.1.beta')  # Change logger
        self.logger.info('Otto Logger is been activated.')
