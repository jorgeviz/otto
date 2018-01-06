""" 
Otto CT main console module

Module to initialize automated trading importing rules from
config file, all connection and validations are done over 
Bitso and BitsoTrade classes located inte th otto.core package.

Status: beta-testing
"""
from __future__ import print_function
import os
import json
from otto.core.bitso_ import BitsoTrade
# from otto.helpers import ottoHelpers  # Need to update to Python3

def main():
    """ Main Method to execute Otto in console
    """
    # Get Bitso Credentials
    _b_key = os.getenv('BITSO_API_KEY')
    _b_secr = os.getenv('BITSO_API_SECRET')
    # Bitso class initialization
    _bitso = BitsoTrade(_b_key, _b_secr)
    # Fetch Config File
    with open('config.json', 'r') as cfg:
        config = json.loads(cfg.read())
    # Set Automatic Trading on
    try:
        _bitso.automate(config)
    except KeyboardInterrupt:
        print('Shutting down...')        

if __name__ == '__main__':
    print('******************************************')
    print('******************************************')
    print('+++++ Initializing OttoCT v0.0.1.beta ++++')
    print('******************************************')
    print('******************************************')
    # Calling Main method
    main()
    print('Done!')
