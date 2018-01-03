# -*- coding: utf-8 -*- 
from __future__ import print_function
import bitso
import requests
from pprint import pformat as pf
import datetime
import csv
# from ..helpers import ottoHelpers  # Need to update to Python3


class Bitso(object):
    """ Class to perform Bitso trades over crypto-currencies
    	and store prices in a local DB for future analysis
    """

    def __init__(self, api_key=None, secret=None):
    	""" Constructor

            Params:
            -----
            - api_key : (str) API KEY provided by Bitso
            - secret : (str) API SECRET provided by Bitso
    	"""
    	if api_key is not None and secret is not None:
    		self.api = bitso.Api(api_key, secret)
    	else:
    		self.api = bitso.Api()
        # Helpers
        # self.oh = ottoHelpers()
        # Show Books
        self.get_books()
        # Show Fees
        self.get_fees()
        # Show Account limits
        self.get_limits()
        # Get Balances

    #def get_auth(self):
        # import time
        # import hmac
        # import hashlib
        # import requests


        # bitso_key = "BITSO_KEY"
        # bitso_secret = "BITSO_SECRET"
        # nonce =  str(int(round(time.time() * 1000)))
        # http_method = "GET"
        # request_path = "/v3/balance/"
        # json_payload = ""

        # # Create signature
        # message = nonce+http_method+request_path+json_payload
        # signature = hmac.new(bitso_secret.encode('utf-8'),
        #                                             message.encode('utf-8'),
        #                                             hashlib.sha256).hexdigest()

        # # Build the auth header
        # auth_header = 'Bitso %s:%s:%s' % (bitso_key, nonce, signature)

        # # Send request
        # response = requests.get("https://api.bitso.com/v3/balance/", headers={"Authorization": auth_header})
        # print response.content

    def get_limits(self):
        """ Method to show account status
        """
        self.acc_status = self.api.account_status()
        print("Daily Limit: $", self.acc_status.daily_limit)
        print("Daily Remaining: $", self.acc_status.daily_remaining, '\n')

    def get_fees(self):
        """ Method to show fees
        """
        _fees = self.api.fees()
        # Obtain JSON of fees
        self.fees = [{_f: float(_fees.__dict__[_f].fee_percent)} \
                    for _f in _fees.__dict__.keys()\
                        if _f in self.books_avail]
        print('Fees:', pf(self.fees), '\n')

    def get_books(self, _show=False):
    	""" Method to show available books in bitso

            Params:
            -----
            - _show : (bool) Show minimum and maximum order values in Bitso
    	"""
        try:
            # Books consultation
            _av_books = requests.get("https://api.bitso.com/v3/available_books/")
        except requests.exceptions.RequestException as _rexc:
            print(_rexc)
            return None
        # Success verification
        if _av_books.json()['success']:
            self.books = _av_books.json()['payload']
        else:
            print('Request has not been successful!')
            return None
        # Results' display 
        if _show:
            print(pf(self.books))
        self.books_avail = [_x['book'] for _x in self.books]
    	print('Available books:', pf(self.books_avail), '\n')


    def price(self, _book):
        """ Method to verify Value of defined Pair of currencies

            Params:
            -----
            - _book : (str) Book or Pair of currencies to verify 

            Returns:
            -----
            - (dict) Pair exchange values
            >>> {
                "book": "btc_mxn",
                "volume": "22.31349615",
                "high": "5750.00",
                "last": "5633.98",
                "low": "5450.00",
                "vwap": "5393.45",
                "ask": "5632.24",
                "bid": "5520.01",
                "created_at": "2016-04-08T17:52:31.000+00:00"
            }            
        """
        try:
            #_p = self.api.ticker(_book)
            _p = requests.get('https://api.bitso.com/v3/ticker/?book={}'.format(_book)).json()
        except Exception as e:
            print(e)
            return None
        # Success verification
        if not _p['success']:
            print('Request has not been successful!')
            return None
        # Save for later analysis
        if not self.save_csv(_p['payload']):
            print('Could not save data into file')
        return _p['payload']


    def save_csv(self, _price):
        """ Method to convert JSON exchange values and save it into CSV dumps

            Params:
            - _price : (dict) Pair exchange values

            Returns:
            - (bool) Saving Status
        """
        try:
            # Verify if file existed
            f = open('data/{}.csv'.format(_price['book']), 'r')
            print('File existed, appending...')
            f.close()
        except IOError:
            # If new file, create headers
            f = open('data/{}.csv'.format(_price['book']), 'w')
            print('Creating file with headers')
            writer = csv.DictWriter(f, fieldnames=list(_price.keys()))
            writer.writeheader()
            print('File created, appending...')
            f.close()
        try:
            f = open('data/{}.csv'.format(_price['book']), 'a')
            writer = csv.DictWriter(f, fieldnames=list(_price.keys()))
            writer.writerow(_price)
            print('Saved price data!')
        except Exception as e:
            print(e)
            return False
        return True