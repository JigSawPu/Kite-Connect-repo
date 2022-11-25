#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 19:13:26 2021

@author: aryakumar
"""

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key='XXXXXXXXXXXX')
print(kite.login_url())

request_token = input('enter req token: ')
data = kite.generate_session(request_token, api_secret='XXXXXXXXXXXXXXXXXXX')
kite.set_access_token(data['access_token'])


instrument_df = pd.DataFrame(kite.instruments("NFO"))

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]

kws = KiteTicker('xxxxxxxxxxxxxxr',kite.access_token)

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    logging.debug(f"Ticks: {ticks}")


def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_QUOTE, tokens)
  
def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()
       
def buy(symbol,qnty):
    kite.place_order(variety=kite.VARIETY_REGULAR, 
                     exchange=kite.EXCHANGE_NFO, 
                     tradingsymbol=symbol, 
                     transaction_type=kite.TRANSACTION_TYPE_BUY, 
                     quantity=qnty, 
                     product=kite.PRODUCT_NRML, 
                     order_type=kite.ORDER_TYPE_MARKET)


def sell(symbol,qnty):
    kite.place_order(variety=kite.VARIETY_REGULAR, 
                     exchange=kite.EXCHANGE_NFO, 
                     tradingsymbol=symbol, 
                     transaction_type=kite.TRANSACTION_TYPE_SELL, 
                     quantity=qnty, 
                     product=kite.PRODUCT_NRML, 
                     order_type=kite.ORDER_TYPE_MARKET)

tickers = ['XXXXXXXXXXXX']
tokens = tokenLookup(instrument_df,tickers)
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()








