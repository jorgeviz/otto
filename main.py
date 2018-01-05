# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import json
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
    # Retrieve all currency-pair prices
    #_bitso.all_prices()
    # Set order
    #curr_pair = "ltc_mxn"
    #_bitso.set_market_order(curr_pair, 'buy', 0.002, only_check=True)
    # Get Balance
    #_bitso.get_balances()
    # Fetch Config File
    with open('config.json', 'r') as cfg:
        config = json.loads(cfg.read())
    # Set Automatic Trading on
    _bitso.automate(config)

if __name__ == '__main__':
    print('\nInitializing OttoCT v0.0.1.beta...', '\n')
    main()
    print('Done!')
