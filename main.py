# -*- coding: utf-8 -*-
from __future__ import print_function
from otto.core._bitso import Bitso
import time
# from otto.helpers import ottoHelpers  # Need to update to Python3

# Global Vars
#_oh = ottoHelpers()
#_oh.logger.info('Helpers are ON!')

def main():
	""" Main Method to execute Otto in console 
	"""
	# Bitso class initialization
	_bitso = Bitso()
	# Bitso available books
	_bitso.books(True)
	# Verify prices of a given pair
	_curr = raw_input('Select currency to monitor: ')
	print(_bitso.price(_curr))

	


if __name__ == '__main__':
	print('Initializing OttoCT v0.0.1.beta...')
	main()
	print('Done!')
