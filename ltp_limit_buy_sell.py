#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 20:05:47 2021

@author: aryakumar
"""

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key='w8rdwxd70igahlor')
print(kite.login_url())

request_token = input('enter req token: ')
data = kite.generate_session(request_token, api_secret='ho7xfopyaqn3d3zt7u36nu5zgkpqhsgg')
kite.set_access_token(data['access_token'])


instrument_df = pd.DataFrame(kite.instruments("NFO"))

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]

kws = KiteTicker('w8rdwxd70igahlor',kite.access_token)
order_no = len(kite.orders()) - 1
entry_price = kite.orders()[order_no]['average_price']
tickers = [kite.orders()[order_no]['tradingsymbol']]
tokens = tokenLookup(instrument_df,tickers)

tickers = ['NATURALGAS21OCTFUT']
tokens = tokenLookup(instrument_df,tickers)

def on_ticks(ws, ticks):
    limit = 400
    # Callback to receive ticks.
    logging.debug(f"Ticks: {ticks}")
    if ticks[0]['last_price'] == limit:
        for ticker in tickers:
            buy(ticker,1)
    buytrail(ticks[0]['last_price'],10,1.20)        

def on_connect(ws, response):
    # Callback on successful connect.
    # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_QUOTE, tokens)
  
def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()
       
def buy(symbol,qnty=1):
    kite.place_order(variety=kite.VARIETY_REGULAR, 
                     exchange=kite.EXCHANGE_NFO, 
                     tradingsymbol=symbol, 
                     transaction_type=kite.TRANSACTION_TYPE_BUY, 
                     quantity=qnty, 
                     product=kite.PRODUCT_MIS, 
                     order_type=kite.ORDER_TYPE_MARKET)


def sell(symbol,qnty=1):
    kite.place_order(variety=kite.VARIETY_REGULAR, 
                     exchange=kite.EXCHANGE_NFO, 
                     tradingsymbol=symbol, 
                     transaction_type=kite.TRANSACTION_TYPE_SELL, 
                     quantity=qnty, 
                     product=kite.PRODUCT_MIS, 
                     order_type=kite.ORDER_TYPE_MARKET)

def buytrail(ltp,sl,pft):
    stoploss_initl = entry_price*(1-(sl/100))
    if ltp > entry_price:
        if ltp >= (pft*entry_price):
            try:
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR, 
                     exchange=kite.EXCHANGE_NFO, 
                     tradingsymbol=kite.orders()[order_no]['tradingsymbol'], 
                     transaction_type=kite.TRANSACTION_TYPE_SELL, 
                     quantity=kite.orders()[order_no]['quantity'], 
                     product=kite.PRODUCT_NRML, 
                     order_type=kite.ORDER_TYPE_MARKET)

                logging.info(f"Order placed. ID is: {order_id}")
            except Exception as e:
                logging.info(f"Order placement failed: {e.message}")
            kws.close()
    else:
        if ltp <= stoploss_initl:
            try:
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR, 
                     exchange=kite.EXCHANGE_NFO, 
                     tradingsymbol=kite.orders()[order_no]['tradingsymbol'], 
                     transaction_type=kite.TRANSACTION_TYPE_SELL, 
                     quantity=kite.orders()[order_no]['quantity'], 
                     product=kite.PRODUCT_NRML, 
                     order_type=kite.ORDER_TYPE_MARKET)

                logging.info(f"Order placed. ID is: {order_id}")
            except Exception as e:
                logging.info(f"Order placement failed: {e.message}")
            kws.close()

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.connect()