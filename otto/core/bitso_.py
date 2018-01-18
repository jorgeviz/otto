# -*- coding: utf-8 -*- 
from __future__ import print_function
import bitso
import requests
from pprint import pformat as pf
import datetime
import csv
import time
import sys
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
        self.get_books() # Set True to show limits
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
        # wait for a sec.
        time.sleep(1)
        print("Daily Limit: $", self.acc_status.daily_limit)
        print("Daily Remaining: $", self.acc_status.daily_remaining, '\n')

    def get_fees(self):
        """ Method to retrieve and show fees
        """
        _fees = self.api.fees()
        # wait for a sec.
        time.sleep(1)
        # Obtain dict of fees
        self.fees = {_f: float(_fees.__dict__[_f].fee_percent) \
                    for _f in _fees.__dict__.keys()\
                        if _f in self.books_avail}
        print('Fees (%):', pf(self.fees), '\n')
    
    def get_balances(self):
        """ Method to retrieve and show account balances
        """
        _balances = self.api.balances()
        # wait for a sec.
        time.sleep(1)
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
            # wait for a sec.
            time.sleep(1)
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
            # wait for a sec.
            time.sleep(1.5)
        except Exception as e:
            print(e)
            return None
        # Success verification
        if not _p['success']:
            print('Request has not been successful!')
            return None
        # Save for later analysis
        if not self.save_csv(_p['payload'], _p['payload']['book']):
            print('Could not save data into file')
        return _p['payload']

    def all_prices(self, valid='all'):
        """ Method to retrieve all prices from valid currencies

            Params:
            -----
            valid: (str | list) 'all' if wants to perform over each currency, otherwise send list of Currency-Pairs
        """
        # Validate currencies
        if valid == 'all':
            _pairs = self.books_avail
        else:
            _pairs = [_v for _v in valid if _v in self.books_avail]
        curr_prices = {}
        # Loop over each currency to retrieve price
        for _c in _pairs:
            max_tries = 3
            for _try in range(max_tries):
                try:
                    curr_prices[_c] = float(self.price(_c)['last'])
                    break
                except TypeError:
                    # In case of type error
                    print('Could not fetch price, retrying...')
                    time.sleep(2)
                    if _try == (max_tries-1):
                        print('Exceeded trials, shutting down!')
                        sys.exit()
            # Wait for 1 sec. to avoid being blocked
            time.sleep(0.5)
        print('Current Currency-Pair prices: \n', pf(curr_prices), '\n')
        return curr_prices
            

    def save_csv(self, _dict, f_name):
        """ Method to convert JSON exchange values and save it into CSV dumps

            Params:
            - _dict: (dict) Data Values
            - f_name: (str) File Name

            Returns:
            - (bool) Saving Status
        """
        try:
            # Verify if file existed
            f = open('data/{}.csv'.format(f_name), 'r')
            print('File existed, appending...')
            f.close()
        except IOError:
            # If new file, write headers
            f = open('data/{}.csv'.format(f_name), 'w')
            print('Creating file with headers')
            writer = csv.DictWriter(f, fieldnames=list(_dict.keys()))
            writer.writeheader()
            print('File created, appending...')
            f.close()
        try:
            # Append data value into File
            f = open('data/{}.csv'.format(f_name), 'a')
            writer = csv.DictWriter(f, fieldnames=list(_dict.keys()))
            writer.writerow(_dict)
            print('Saved {} data!'.format(f_name))
        except Exception as e:
            print(e)
            return False
        return True


class BitsoTrade(Bitso):
    """ Class to perform trades over Bitso exchange, which inheritates
        all methods from Bitso class.

        BitsoTrade attrs:
        - trade_prices: (dict) Dictionary of last prices indexed by Currency-pairs
        - base_lines: (dict) Dictionary of base_line indexed by Currency_pairs
    """
    
    def __init__(self, api_key, secret):
        """ Constructor 
        """
        # Initialize Bitso Parent Class
        super(BitsoTrade, self).__init__(api_key, secret)
        self.trade_prices = {}
        self.base_lines = {}

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
        # Compare if above minimum amount
        if float(amount) < float(_tbook['minimum_amount']):
            print('{} is too small to perform transaction'.format(amount))
            return False
        # Compare if below maximum amount
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
            print('Selling, so checking Major to verify balance')
            if amount > self.balances[_selling]['available']:
                print('Balance {} in {} is not enough to perform transaction for {}'
                    .format(self.balances[_selling]['available'],
                            _selling,
                            amount))
                return None
            print('Balance {} in {} enough to sell {}'
                .format(self.balances[_selling]['available'],
                        _selling,
                        amount))
            return self.balances[_selling]['available']
        # If selling minor, get last price of exchange between currencies
        exc_price = self.price(_pair)
        tmp_balance = self.balances[_selling]['available']
        # Converting minor into Major currency equivalence to validate correct balance
        print('Buying, so converting minor into Major to verify balance')
        if (amount * float(exc_price['last'])) > tmp_balance:
                print('{} is not enough balance in {} to perform transaction for {}'
                    .format(tmp_balance,
                            _selling,
                            amount * float(exc_price['last'])))
                return None
        print('Balance {} in {} enough to sell {}'
                .format(tmp_balance,
                        _selling,
                        amount * float(exc_price['last'])))
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
            - only_check: (bool) Set False if want to execute order, 
            otherwise just verifies if is a valid transaction
            
            Returns:
            -----
            - (bool) Transaction Status
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
                # wait for some seconds...
                time.sleep(3)
                _transac.update({
                    'book': _pair,
                    'side': _side,
                    'order_type': 'market',
                    'major': str(_major_amount),
                    'created_at': str(datetime.datetime.utcnow())
                })
                print('Transaction correctly executed!')
                # Save Transaction into file
                if not self.save_csv(_transac, 'transactions'):
                    print('Could not save transactional data.')
            except Exception as e:
                print('Could not execute transaction:', e)
                return False
        return True

    def update_series(self, valid):
        """ Method to cache prices from valid currencies

            Params:
            -----
            valid: (str | list) 'all' if wants to perform over each currency, otherwise send list of Currency-Pairs
        """
        if valid != 'all' and not isinstance(valid, list):
            print('Valid Pairs param has incorrect format!')
            sys.exit()
        self.trade_prices = self.all_prices(valid)
        print('Trade prices successfully updated!')

    def set_baseline(self, pair):
        """ Method to set baseline to certain currency-pair using last known price

            Params:
            -----
            - pair: (str) Currency-Pair
        """
        if pair not in self.books_avail:
            print('{} Pair is not supported!'.format(pair))
            sys.exit()
        self.base_lines.update({
            pair: self.trade_prices[pair]
        })
        print('{} baseline successfully updated!'.format(pair))

    def config_valid(self, config):
        """ Method to verify if config object is valid

            Params:
            -----
            - config: (dict) JSON file with all needed trade rules

            Returns:
            -----
            - (bool) Config Validation
        """
        if 'valid_pairs' not in config:
            print('Valid Pairs param is missing!')
            sys.exit()
        if 'rules' not in config:
            print('Valid Pairs param is missing!')
            sys.exit()
        if (set(config['rules'].keys()) != set(config['valid_pairs'])) or \
                (len(config['rules'].keys()) != len(config['valid_pairs'])):
            print('Valid Pairs and Rules must match!')
            sys.exit()
        return True

    def evaluate_rule(self, pair, rule):
        """ Method to evaluate which action must be executed after defined rules.
            * If trading_price > (base_line + rule_buying_bound) Then: buy
            * Else if trading_price < (base_line + rule_selling_bound) Then: sell
            * Else: None

            Params:
            -----
            - pair: (str) Currency Pair
            - rule: (dict) Rule with selling and buying bounds

            Returns:
            -----
            - (str | NoneType) Trading Position ('buy' | 'sell' | None)
        """
        # Boundaries
        upper_bound = self.base_lines[pair] + (self.base_lines[pair] * rule['buying_major_bound'])
        lower_bound = self.base_lines[pair] + (self.base_lines[pair] * rule['selling_major_bound'])
        # Selling evaluation
        if self.trade_prices[pair] > upper_bound:
            print('Buying: {} is MORE EXPENSIVE than {}'.format(self.trade_prices[pair], self.base_lines[pair]))
            return 'buy'
        elif self.trade_prices[pair] < lower_bound:
            print('Selling: {} is CHEAPER than {}'.format(self.trade_prices[pair], self.base_lines[pair]))
            return 'sell'
        else:
            print('Nothing: {} is almost the same than {}'.format(self.trade_prices[pair], self.base_lines[pair]))
            print('Decision:   {}   >   {}   <    {}'.format(lower_bound, self.trade_prices[pair], upper_bound))
            return None

    def get_acumulate(self):
        """ Method to show Acumulated Balance and store results
        """
        # Update Balances
        self.get_balances()
        # Total Balances dictionary
        b_dict = {_k+'_total': _v['total'] for _k,_v in self.balances.items()}
        # MXN equivalences
        mxn_equivs = []
        for _k, _v in self.balances.items():
            if _k == 'mxn':
                # Append MXN Peso
                mxn_equivs.append(_v['total'])
                continue
            for _ba in self.books_avail:
                if _k+'_mxn' == _ba:
                    # Append Direct MXN convertion
                    mxn_equivs.append(_v['total'] * self.trade_prices[_ba])
                    break
                if _k+'_btc' == _ba:
                    # Append BTC-MXN convertion
                    mxn_equivs.append(_v['total'] 
                                    * self.trade_prices[_ba]
                                    * self.trade_prices['btc_mxn'])
                    break                
        # Update acumulate in dict
        b_dict['acumulated_mxn'] = sum(mxn_equivs)
        b_dict['created_at'] = str(datetime.datetime.utcnow())
        print(""" Acumulated Balances: 
        ----
        ----
        {}
        ----
        ----
        """.format(pf(b_dict)))
        # Write balance in file   
        self.save_csv(b_dict, 'balances')

    def automate(self, config):
        """ Method to apply orders within defined rules in the config file.

            Params:
            - config: (dict) JSON file with all needed trade rules
            >>> {
                'valid_pairs': ['btc_mxn', 'eth_mxn'],
                'rules': {
                    'btc_mxn':{
                        'selling_major_bound': 3,  # In %
                        'buying_major_bound': -1.8,  # In %
                        'major_amount' : 0.00003
                    },
                    'eth_mxn':{
                        'selling_major_bound': 2,  # In %
                        'buying_major_bound': -1.8,  # In %
                        'major_amount' : 0.003
                    }
                }
            }
        """
        # Validate Config file
        self.config_valid(config)
        # Initialize
        self.update_series(config['valid_pairs'])
        # For each currency-pair
        for vp in config['valid_pairs']:
            # Set Baseline
            self.set_baseline(vp)
        try:
            while True:
                # Performance Delay
                time.sleep(2)  # Set to 2 secs.
                # Update Price Series
                self.update_series(config['valid_pairs'])
                print()
                # For each currency-pair 
                for vp in config['valid_pairs']:
                    # Evaluate action
                    print('Evaluating {}...'.format(vp))
                    _action = self.evaluate_rule(vp, config['rules'][vp])
                    if not _action:
                        # Passing action
                        print('Not action required!')
                        continue
                    print("################################################")
                    print("################################################")
                    print('Trying to perform {} in {}'.format(_action, vp))
                    # If exceeds limits, perform order
                    self.set_market_order(vp,
                                    _action,
                                    config['rules'][vp]['major_amount'],
                                    only_check=False)  # To actually perform Orders, set False
                    print("################################################")
                    print("################################################")                    
                    # Reset Baseline
                    self.set_baseline(vp)
                    # Get Acum Balances
                    self.get_acumulate()
                print()
        except KeyboardInterrupt:
            print('\n Stoping trading!!!')
            import sys 
            sys.exit()