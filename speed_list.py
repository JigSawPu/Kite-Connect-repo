#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 11:09:41 2021

@author: aryakumar
"""

from kiteconnect import KiteConnect, KiteTicker
import pandas as pd
import logging
import time
import os
import matplotlib.pyplot as plt
import copy

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key='XXXXXXXXXX')
request_token = input('enter req token link: ').split('request_token=')[1][:32]
data = kite.generate_session(request_token, api_secret='XXXXXXXXXXXXXXXXXX')
kite.set_access_token(data['access_token'])
instrument_df = pd.DataFrame(kite.instruments("NSE"))

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]

kws = KiteTicker('XXXXXXXXXX',kite.access_token)

tickers = [input('enter ticker: ')]
#speed_limit = int(input('enter speed limit for ticker: '))
tokens = tokenLookup(instrument_df,tickers)

time_stamp_price_list = []
time_diff_list = [(time.perf_counter(),kite.ltp(f'NSE:{tickers[0]}')[f'NSE:{tickers[0]}']['last_price'])]
speed = []

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

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
        velo = (time_diff_list[-1][1] - time_diff_list[-2][1])/(time_diff_list[-1][0] - time_diff_list[-2][0])
        speed.append(velo*300) #this calculates change in price every 5 min, 
        plt.plot(speed)
        plt.tight_layout()
        plt.show()# if (speed[-1]*300) > 30:
        #     notify(f'{tickers[0]} speed alert', f'Speed Crossed set limit\n Current speed is {speed[-1]*300} every 5 min')

    
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.connect()

# plt.plot(speed)
# abs_speed = speed.copy()
# for i in range(0,54):
#     abs_speed[i] = abs(abs_speed[i])
# plt.plot(abs_speed)

