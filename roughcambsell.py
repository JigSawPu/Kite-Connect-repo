#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 13:18:58 2021

@author: aryakumar
"""

import pandas as pd
from kiteconnect import KiteConnect, KiteTicker
from yahoofinancials import YahooFinancials
import datetime as dt
import logging

kite = KiteConnect(api_key='w8rdwxd70igahlor')
request_token = input('enter req token link: ').split('request_token=')[1][:32]
data = kite.generate_session(request_token, api_secret='ho7xfopyaqn3d3zt7u36nu5zgkpqhsgg')
kite.set_access_token(data['access_token'])
instrument_df = pd.DataFrame(kite.instruments("NFO"))

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]

kws = KiteTicker('w8rdwxd70igahlor',kite.access_token)
tickers = []
tokens = tokenLookup(instrument_df,tickers)
end = dt.date.today().strftime('%Y-%m-%d')
start = (dt.date.today() - dt.timedelta(10)).strftime('%Y-%m-%d')
ohlc_day = pd.DataFrame()
for ticker in tickers:
    yahoo_financials = YahooFinancials(ticker)
    json = yahoo_financials.get_historical_price_data(start, end, 'daily')
    ohlv = json[ticker]['prices']
    temp = pd.DataFrame(ohlv)[['formatted_date', 'open', 'high', 'low', 'close']]
    temp.set_index('formatted_date', inplace=True)
    temp.dropna(inplace=True)
    ohlc_day = temp


def cam_levels(ohlc_day):
    high = round(ohlc_day["high"][-1], 2)
    low = round(ohlc_day["low"][-1], 2)
    close = round(ohlc_day["close"][-1], 2)
    range = high - low
    h4 = close + range*(1.1/2)
    h3 = close + range*(1.1/4)
    h2 = close + range*(1.1/6)
    h1 = close + range*(1.1/12)
    pivot = round((high + low + close)/3, 2)
    l1 = close - range*(1.1/12)
    l2 = close - range*(1.1/6)
    l3 = close - range*(1.1/4)
    l4 = close - range*(1.1/2)
    return {'h4': h4,
            'h3': h3,
            'h2': h2,
            'h1': h1,
            'pivot': pivot,
            'l1': l1,
            'l2': l2,
            'l3': l3,
            'l4': l4}


pplevels = cam_levels(ohlc_day)


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
    auto_cam_bsell(pplevels, ticks[0]['last_price'])
    
def auto_cam_bsell(pplevels, ticks):
    if ticks > 0.999*pplevels.h3:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NFO,
                                        tradingsymbol=tickers[0],
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=kite.orders()[order_no]['quantity'],
                                        product=kite.PRODUCT_NRML,
                                        order_type=kite.ORDER_TYPE_MARKET)
            logging.info(f"Order placed. ID is: {order_id}")
        except Exception as e:
            logging.info(f"Order placement failed: {e.message}")

    elif ticks < 1.001*pplevels.l3:
        buy()
        kws.close()

kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.connect()