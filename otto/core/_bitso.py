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

    def books(self, _show=False):
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
    	print('Available books:', self.books_avail)


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