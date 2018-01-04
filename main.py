# -*- coding: utf-8 -*-
from __future__ import print_function
# import time
import os
from otto.core.bitso_ import BitsoTrade
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
    _bitso = BitsoTrade(_b_key, _b_secr)
    # Verify prices of a given pair
    curr_pair = "ltc_mxn"  # Change this to verify all
    print('Requesting last {} price...'.format(curr_pair))
    print('Last {} price'.format(curr_pair), _bitso.price(curr_pair)['last'])
    # Set order
    _bitso.set_market_order(curr_pair, 'buy', 0.002, only_check=True)

if __name__ == '__main__':
    print('Initializing OttoCT v0.0.1.beta...', '\n')
    main()
    print('Done!')
