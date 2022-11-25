#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 17:55:08 2021

@author: aryakumar
"""

from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import pandas as pd
import logging
import time
from datetime import datetime
import matplotlib.pyplot as plt
from itertools import count
from matplotlib.animation import FuncAnimation
import random
import sys

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key='w8rdwxd70igahlor')
print(kite.login_url())

request_token = input('enter req token: ')
data = kite.generate_session(request_token, api_secret='ho7xfopyaqn3d3zt7u36nu5zgkpqhsgg')
kite.set_access_token(data['access_token'])


#instrument_df = pd.DataFrame(kite.instruments("NFO"))
mcx_inst_df = pd.DataFrame(kite.instruments("MCX"))

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]

kws = KiteTicker('w8rdwxd70igahlor',kite.access_token)


plt.style.use('fivethirtyeight')
x_vals = []
y_vals = []
index = count()
def animate(ltp):
    x_vals.append(next(index))
    y_vals.append(ltp)
    plt.plot(x_vals, y_vals)
    

# ani = FuncAnimation(plt.gcf(), animate, interval=1000)
# plt.tight_layout()
# plt.show()

def on_ticks(ws, ticks):
    # Callback to receive ticks.
    logging.debug(f"Ticks: {ticks}")
    # print(ticks)
    ltp = ticks[0]['last_price'] 
    # print(datetime.now().strftime("%H:%M:%S:%f"))
    # print(ticks[0]['last_price'])
    # time.sleep(30)
    #buytrail(15,ltp)
    #selltrail(15,ltp)
    def animate(ltp):
        x_vals.append(datetime.now().strftime("%H:%M:%S:%f"))
        y_vals.append(ltp)
        plt.plot(x_vals, y_vals)
    ani = FuncAnimation(plt.gcf(), animate(ltp), interval=1000)
    plt.tight_layout()
    plt.show()


#datetime.now().strftime("%H:%M:%S")

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
                     product=kite.PRODUCT_MIS, 
                     order_type=kite.ORDER_TYPE_MARKET)


def sell(symbol,qnty):
    kite.place_order(variety=kite.VARIETY_REGULAR, 
                     exchange=kite.EXCHANGE_NFO, 
                     tradingsymbol=symbol, 
                     transaction_type=kite.TRANSACTION_TYPE_SELL, 
                     quantity=qnty, 
                     product=kite.PRODUCT_MIS, 
                     order_type=kite.ORDER_TYPE_MARKET)


# def buytrail(order_no,ltp,sl,pft):
    
#      # get price from orders
    
#     if ltp > entry_price:
#         #stoploss_dyna = stoploss_initl + ltp - entry_price
#         stoploss_initl = entry_price*(1-(sl/100))
#         if ltp >= (pft*entry_price):
#             if kite.orders()[order_no]['transaction_type'] == 'BUY':
#                 sell(kite.orders()[order_no]['tradingsymbol'],kite.orders()[order_no]['quantity'])
#                 sys.exit()
#             else:
#                 buy(kite.orders()[order_no]['tradingsymbol'],kite.orders()[order_no]['quantity'])
#                 sys.exit()
#     else:
#         #stoploss_dyna = stoploss_initl
#         if ltp <= stoploss_initl:
#             if kite.orders()[order_no]['transaction_type'] == 'BUY':
#                 sell(kite.orders()[order_no]['tradingsymbol'],kite.orders()[order_no]['quantity'])
#                 sys.exit()
#             else:
#                 buy(kite.orders()[order_no]['tradingsymbol'],kite.orders()[order_no]['quantity'])
#                 sys.exit()

# def selltrail(order_no,ltp,sl,pft):
#     if ltp < entry_price:
#         #stoploss_dyna = stoploss_initl + ltp - entry_price
#         stoploss_initl = entry_price*(1+(sl/100))
#         if ltp <= (pft*entry_price):
#             if kite.orders()[order_no]['transaction_type'] == 'BUY':
#                 sell(kite.orders()[order_no]['tradingsymbol'],kite.orders()[order_no]['quantity'])
#                 sys.exit()
#             else:
#                 buy(kite.orders()[order_no]['tradingsymbol'],kite.orders()[order_no]['quantity'])
#                 sys.exit()
#     else:
#         #stoploss_dyna = stoploss_initl
#         if ltp >= stoploss_initl:
#             if kite.orders()[order_no]['transaction_type'] == 'BUY':
#                 sell(kite.orders()[order_no]['tradingsymbol'],kite.orders()[order_no]['quantity'])
#                 sys.exit()
#             else:
#                 buy(kite.orders()[order_no]['tradingsymbol'],kite.orders()[order_no]['quantity'])
# #                 sys.exit()
# def on_ticks(ws, ticks):
#     # Callback to receive ticks.
#     logging.debug(f"Ticks: {ticks}")
#     # print(ticks)
#     ltp = ticks[0]['last_price'] 
#     # print(datetime.now().strftime("%H:%M:%S:%f"))
#     # print(ticks[0]['last_price'])
#     # time.sleep(30)
#     buytrail(15,ltp,10,1.20)
#     #selltrail(15,ltp,10,0.80)
#     # def animate(ltp):
#     #     x_vals.append(datetime.now().strftime("%H:%M:%S:%f"))
#     #     y_vals.append(ltp)
#     #     plt.plot(x_vals, y_vals)
#     # ani = FuncAnimation(plt.gcf(), animate(ltp), interval=1000)
#     # plt.tight_layout()-
#     # plt.show()
# entry_price = kite.orders()[15]['average_price']
tickers = ['NATURALGAS21DECFUT']
tokens = tokenLookup(mcx_inst_df,tickers)
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect()





















