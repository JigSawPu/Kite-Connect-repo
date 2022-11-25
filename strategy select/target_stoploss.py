#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 13:18:58 2021

@author: aryakumar
"""
from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import logging
import os

def target_sl(buy_or_sell, target, stoploss):
    logging.basicConfig(level=logging.DEBUG)
    cwd = os.chdir("/home/ec2-user/strategy select/")
    kite = KiteConnect(api_key='ddoyhzsgrte3dq3s')
    access_token = open('access_token.txt','r').read().split()[-1]
    kite.set_access_token(access_token)
    instrument_df = pd.DataFrame(kite.instruments("NFO"))

    def tokenLookup(instrument_df,symbol_list):
        return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                    .instrument_token.values[0])for symbol in symbol_list]


    kws = KiteTicker('ddoyhzsgrte3dq3s',kite.access_token)
    order_no = len(kite.orders()) - 1
    entry_price = kite.orders()[order_no]['average_price']
    tickers = [kite.orders()[order_no]['tradingsymbol']]
    tokens = tokenLookup(instrument_df,tickers)

    def on_connect(ws, response):
        # Callback on successful connect.
        # Subscribe to a list of instrument_tokens (RELIANCE and ACC here).
        ws.subscribe(tokens)
        ws.set_mode(ws.MODE_QUOTE, tokens)

    def on_close(ws, code, reason):
        # On connection close stop the main loop
        # Reconnection will not happen after executing `ws.stop()`
        ws.stop()
        
    def on_ticks(ws, ticks):
        # Callback to receive ticks.
        logging.debug(f"Ticks: {ticks}")
        trailer(ticks[0]['last_price'], buy_or_sell)
    
    def trailer(ltp, buy_or_sell):
        if buy_or_sell == 'b':
            if ltp >= target or ltp <= stoploss:
                sell()
                kws.close()
        else:
            if ltp <= target or ltp >= stoploss:
                buy()
                kws.close()


    def sell():
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

    
    def buy():
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR, 
                                        exchange=kite.EXCHANGE_NFO, 
                                        tradingsymbol=kite.orders()[order_no]['tradingsymbol'], 
                                        transaction_type=kite.TRANSACTION_TYPE_BUY, 
                                        quantity=kite.orders()[order_no]['quantity'], 
                                        product=kite.PRODUCT_NRML,
                                        order_type=kite.ORDER_TYPE_MARKET)
            logging.info(f"Order placed. ID is: {order_id}")
        except Exception as e:
            logging.info(f"Order placement failed: {e.message}")
    

    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.connect()