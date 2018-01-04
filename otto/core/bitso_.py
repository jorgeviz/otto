# -*- coding: utf-8 -*- 
from __future__ import print_function
import bitso
import requests
from pprint import pformat as pf
import datetime
import csv
import time
# from ..helpers import ottoHelpers  # Need to update to Python3


class Bitso(object):
    """ Class to perform Bitso trades over crypto-currencies
    	and store prices in a local DB for future analysis.

        Bitso Class attrs:

        - api : (bitso.Api) Bitso API object with authentification
        - acc_status : (bitso.AccountStatus) Bitso Account Status object 
        - books : (list) Dictionaries with trading limits of each Currency-Pair
        - books_avail : (list) Keys of all available Currency-Pairs in Bitso
        - fees : (dict) Trading Fee in percentage indexed by Currency-Pair key
        - balances : (dict) Total and Available balances indexed by Currency key
        - currencies : (list) Available currencies 
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
        # Show Books
        self.get_books(True) # Set True to show limits
        # Show Fees
        self.get_fees()
        # Show Account limits
        self.get_limits()
        # Get Balances
        self.get_balances()

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
        """ Method to retrieve and show account status
        """
        self.acc_status = self.api.account_status()
        print("Daily Limit: $", self.acc_status.daily_limit)
        print("Daily Remaining: $", self.acc_status.daily_remaining, '\n')

    def get_fees(self):
        """ Method to retrieve and show fees
        """
        _fees = self.api.fees()
        # Obtain dict of fees
        self.fees = {_f: float(_fees.__dict__[_f].fee_percent) \
                    for _f in _fees.__dict__.keys()\
                        if _f in self.books_avail}
        print('Fees (%):', pf(self.fees), '\n')
    
    def get_balances(self):
        """ Method to retrieve and show account balances
        """
        _balances = self.api.balances()
        self.currencies = _balances.currencies
        self.balances = {_b: {
                            'available': float(_bv.__dict__['available']),
                            'total': float(_bv.__dict__['total'])
                            } \
                        for _b, _bv in _balances.__dict__.items() \
                            if _b != 'currencies'}
        print('Currencies: ', pf(self.currencies), '\n')
        print('Balances: ', pf(self.balances), '\n')

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
            # Retrieve Book
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
            # If new file, write headers
            f = open('data/{}.csv'.format(_price['book']), 'w')
            print('Creating file with headers')
            writer = csv.DictWriter(f, fieldnames=list(_price.keys()))
            writer.writeheader()
            print('File created, appending...')
            f.close()
        try:
            # Append price value into File
            f = open('data/{}.csv'.format(_price['book']), 'a')
            writer = csv.DictWriter(f, fieldnames=list(_price.keys()))
            writer.writerow(_price)
            print('Saved price data!')
        except Exception as e:
            print(e)
            return False
        return True


class BitsoTrade(Bitso):
    """ Class to perform trades over Bitso exchange
    """
    
    def __init__(self, api_key, secret):
        """ Constructor 
        """
        # Initialize Bitso Parent Class
        super(BitsoTrade, self).__init__(api_key, secret)

    def in_bounds(self, amount, _pair):
        """ Method to check if transaction is within trading bounds in Bitso
            For Book Limits:
            - minimum_amount: Minimum amount of major when placing an order.
            - maximum_amount: Maximum amount of major when placing an order.

            Params:
            -----
            - amount : (float) Amount of Major currency to Trade
            - _pair: (str) Currency-Pair key

            Returns:
            -----
            - (bool) : Valid or not.
        """
        # Verify if is valid currency-pair
        if _pair not in self.books_avail:
            print('{} is not a valid Currency-Pair'.format(_pair))
            return False
        # Fetch book limit info
        _tbook = [_b for _b in self.books if _pair == _b['book']][0]
        # Compare is above minimum amount
        if float(amount) < float(_tbook['minimum_amount']):
            print('{} is too small to perform transaction'.format(amount))
            return False
        # Compare is below maximum amount
        if float(amount) > float(_tbook['maximum_amount']):
            print('{} is too big to perform transaction'.format(amount))
            return False
        return True

    def fetch_currency(self, _pair, _side):
        """ Method to return the correct currency definition to verify in limits

            Params:
            -----
            - _pair: (str) Currency-Pair to Trade (Major_minor)
            - _side: (str, 'buy' | 'sell')  Trading Position

            Returns:
            -----
            - (dict) Corresponding currency to buy and sell
        """
        if _side == 'buy':
            return {
                "buying": _pair.split('_')[0],
                "selling": _pair.split('_')[1]
            }
        else:
            return {
                "buying": _pair.split('_')[1],
                "selling": _pair.split('_')[0]
            }
    
    def enough_balance(self, amount, _pair, _selling):
        """ Method to verify there is enough balance in the selling currency
            to proceed with the transaction.

            Params:
            -----
            - amount: (str) Major amount to Trade
            - _pair: (str) Currency-pair
            - _selling: (float) Selling currency

            Returns:
            -----
            - (float) Current balance of the selling currency
            - (NoneType) In case there is not enough money to execute transaction
        """
        # Update Balances 
        self.get_balances()
        # If selling major compute balance directly
        if _selling == _pair.split('_')[0]:
            # If not enough balance
            if amount > self.balances[_selling]['available']:
                print('{} is not enough balance in {} to perform transaction'
                    .format(self.balances[_selling]['available'],
                            _selling))
                return None
        # If selling minor, get last price of exchange between currencies
        exc_price = self.price(_pair)
        tmp_balance = self.balances[_selling]['available']
        # Converting minor into Major currency equivalence to validate correct balance
        if (amount * float(exc_price['last'])) > tmp_balance:
                print('{} is not enough balance in {} to perform transaction'
                    .format(tmp_balance,
                            _selling))
                return None
        return tmp_balance


    def verify_trade(self, _pair, _side, _major_amount):
        """ Method to verify following transaction has enough balance and is big enough.
        """
        # Fetch currency definition depending on trading position
        _curr = self.fetch_currency(_pair, _side)
        # Check buying currency amount is in book limits
        if not self.in_bounds(_major_amount, _pair):
            return False
        # Check if there is enough balance in the selling currency
        _bal = self.enough_balance(_major_amount, _pair, _curr['selling'])
        if not _bal:
            return False
        print("""Transaction pre-verified!!
        ---
        Buying {} of {}.
        Current {} selling balance is {}.
        ---
        """.format(_major_amount,
            _curr['buying'],
            _curr['selling'],
            _bal
        ))
        return True

    
    def set_market_order(self, _pair, _side, _major_amount, only_check=True):
        """ Method to place a Market order into Bitso for given Currency-Pair 
            and a defined Major amount.

            Trading positions:
            - Buy :  converts minor into Major currency
            - Sell : converts Major into minor currency

            Params:
            -----
            - _pair: (str) Currency-Pair to Trade (Major_minor)
            - _side: (str, 'buy' | 'sell')  Trading Position
            - _major_amount: (float) Major amount to trade
        """
        print("""Executing transaction:
        ---
        Currency-Pair: {}
        Position: {}
        Major Amount: {}
        ---
        """.format(_pair, _side, _major_amount))
        # Verify trade
        if not self.verify_trade(_pair, _side, _major_amount):
            print('Transaction cannot be executed')
            return False
        print('Performing Transaction.....')
        # Execute transaction
        if not only_check:
            try:
                _transac = self.api.place_order(book=_pair,
                                        side=_side,
                                        order_type='market',
                                        major=str(_major_amount))
                _transac.update({
                    'book': _pair,
                    'side': _side,
                    'order_type': 'market',
                    'major': str(_major_amount)
                })
                print('Transaction correctly executed!')
                # Save Transaction into file
                if not self.save_transac(_transac):
                    print('Could not save transactional data.')
            except Exception as e:
                print('Could not execute transaction:', e)
                return False
        # wait for some seconds...
        time.sleep(3)
        return True

    def save_transac(self, _transac):
        """ Method to convert dict transaction values and save it into CSV dumps

            Params:
            - _transac : (dict) Transaction values

            Returns:
            - (bool) Saving Status
        """
        try:
            # Verify if file existed
            f = open('data/transactions.csv', 'r')
            print('File existed, appending...')
            f.close()
        except IOError:
            # If new file, write headers
            f = open('data/transactions.csv', 'w')
            print('Creating file with headers')
            writer = csv.DictWriter(f, fieldnames=list(_transac.keys()))
            writer.writeheader()
            print('File created, appending...')
            f.close()
        try:
            # Append price value into File
            f = open('data/transactions.csv', 'a')
            writer = csv.DictWriter(f, fieldnames=list(_transac.keys()))
            writer.writerow(_transac)
            print('Saved transaction data!')
        except Exception as e:
            print(e)
            return False
        return True