#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 13:54:22 2021

@author: arya
"""
import yfinance as yf
import pandas as pd
from kiteconnect import KiteConnect, KiteTicker
import logging
import time

logging.basicConfig(level=logging.DEBUG)

data = yf.download('^NSEI', period='1mo', interval="15m")
data.drop('Adj Close', axis=1, inplace=True)

def MACD(DF, a=12 ,b=26, c=9):
    """function to calculate MACD
       typical values a(fast moving average) = 12; 
                      b(slow moving average) =26; 
                      c(signal line ma window) =9"""
    df = DF.copy()
    df["ma_fast"] = df["Close"].ewm(span=a, min_periods=a).mean()
    df["ma_slow"] = df["Close"].ewm(span=b, min_periods=b).mean()
    df["macd"] = df["ma_fast"] - df["ma_slow"]
    df["signal"] = df["macd"].ewm(span=c, min_periods=c).mean()
    return df.loc[:,["macd","signal"]]


macd = MACD(data)
macd['histogram'] = macd['macd'] - macd['signal']

kite = KiteConnect(api_key='xxxxxxxxxxxxxx')
request_token = input('enter req token link: ').split('request_token=')[1][:32]
data = kite.generate_session(request_token, api_secret='xxxxxxxxxxxxxxxxxxxx')
kite.set_access_token(data['access_token'])
instrument_df = pd.DataFrame(kite.instruments("NSE"))

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]

kws = KiteTicker('xxxxxxxxxxxx',kite.access_token)

tickers = ['NIFTY 50']
tokens = tokenLookup(instrument_df,tickers)

time_stamp_price_list = []
time_diff_list = [(time.perf_counter(),kite.ltp(f'NSE:{tickers[0]}')[f'NSE:{tickers[0]}']['last_price'])]

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
    time_stamp_price_list.append((time.perf_counter(),ticks[0]['last_price']))
    if (time_stamp_price_list[-1][0] - time_diff_list[-1][0]) >= 300:
        time_diff_list.append((time_stamp_price_list[-1][0],time_stamp_price_list[-1][1]))


kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.connect()
