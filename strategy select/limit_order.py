#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#limit order and trail

from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import logging
import target_stoploss
import trailing
import os

cwd = os.chdir("/home/ec2-user/strategy select/")

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key='xxxxxxxxxxxx')
request_token=input('enter req token link: ').split('request_token=')[1][:32]
data = kite.generate_session(request_token, api_secret='xxxxxxxxxxxxxxxxxxxxxxxxx')
with open('access_token.txt', 'w') as file:
        file.write(data["access_token"])
kite.set_access_token(data['access_token'])
instrument_df = pd.DataFrame(kite.instruments("NFO"))

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]

kws = KiteTicker('xxxxxxxxxxxxx',kite.access_token)
buy_or_sell = input('b for buy & s for sell ?: ').lower()
limit = float(input('enter the price: '))
quantity = int(input('enter quantity: '))
trading_symbol = input('enter trading symbol: ').upper()
print('1 for limit price entry with target_sl!\n')
print('2 for limit price entry with trailing!\n')
strategy_no = int(input('enter what strategy ?: '))
if strategy_no == 1:
    target = float(input('entr the target percent: '))
    stoploss = float(input('entr the stoploss percent: '))
if strategy_no == 2:
    trailer_percent = float(input('enter trailer percent: '))
tickers = [trading_symbol]
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
    ltp = ticks[0]['last_price']
    if buy_or_sell == 'b' and ltp <= limit:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR, 
                                        exchange=kite.EXCHANGE_NFO, 
                                        tradingsymbol=trading_symbol, 
                                        transaction_type=kite.TRANSACTION_TYPE_BUY, 
                                        quantity=quantity, 
                                        product=kite.PRODUCT_NRML, 
                                        order_type=kite.ORDER_TYPE_MARKET)
            logging.info(f"Order placed. ID is: {order_id}")
        except Exception as e:
            logging.info(f"Order placement failed: {e.message}")
        kws.close()
        if strategy_no == 1:
            target_stoploss.target_sl(buy_or_sell, target, stoploss)
        if strategy_no == 2:
            trailing.connect_and_trailer(buy_or_sell, trailer_percent)

    if buy_or_sell == 's' and ltp >= limit:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR, 
                                        exchange=kite.EXCHANGE_NFO, 
                                        tradingsymbol=trading_symbol, 
                                        transaction_type=kite.TRANSACTION_TYPE_SELL, 
                                        quantity=quantity, 
                                        product=kite.PRODUCT_NRML, 
                                        order_type=kite.ORDER_TYPE_MARKET)
            logging.info(f"Order placed. ID is: {order_id}")
        except Exception as e:
            logging.info(f"Order placement failed: {e.message}")
        kws.close()
        if strategy_no == 1:
            target_stoploss.target_sl(buy_or_sell, target, stoploss)
        if strategy_no == 2:
            trailing.connect_and_trailer(buy_or_sell, trailer_percent)


kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.connect()