#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 13:43:11 2021

@author: aryakumar
"""

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import logging
import sqlite3

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key='XXXXXXXXX')
request_token = input('enter req token link: ').split('request_token=')[1][:32]
data = kite.generate_session(request_token, api_secret='XXXXXXXXXXXXXXXXX')
kite.set_access_token(data['access_token'])
instrument_df = pd.DataFrame(kite.instruments("NSE"))

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]

kws = KiteTicker('XXXXXXXXXX',kite.access_token)

tickers = [input('enter ticker: ')]
#speed_limit = int(input('enter speed limit for ticker: '))
tokens = tokenLookup(instrument_df,tickers)