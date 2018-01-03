# -*- coding: utf-8 -*-
from __future__ import print_function
from otto.core._bitso import Bitso
import time
import os
# from otto.helpers import ottoHelpers  # Need to update to Python3

# Global Vars
#_oh = ottoHelpers()
#_oh.logger.info('Helpers are ON!')

def main():
    """ Main Method to execute Otto in console
    """
    # Get Bitso Credentials
    _b_key = os.getenv('BITSO_API_KEY')
    _b_secr = os.getenv('BITSO_API_SECRET')
    # Bitso class initialization
    _bitso = Bitso(_b_key, _b_secr)
    # Verify prices of a given pair
    _curr = "eth_mxn"  # Change this to verify all
    print('Requesting {} price...'.format(_curr))
    from pprint import pprint
    pprint(_bitso.price(_curr))


if __name__ == '__main__':
    print('Initializing OttoCT v0.0.1.beta...')
    main()
    print('Done!')
