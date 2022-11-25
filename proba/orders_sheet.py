#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 13:18:58 2021

@author: aryakumar
"""

import numpy as np
import pandas as pd
import yfinance as yf
from kiteconnect import KiteConnect
import openpyxl

kite = KiteConnect(api_key='XXXXXXXXXX')
access_token = 'XXXXXXXXXXXXXXXXXXXXXX'
kite.set_access_token(access_token)
nifty, dummy_var1 = yf.download('^NSEI', period='1d', interval="1m"), yf.download('^XXXXXX', period='1d', interval="1m")
nifty.index = pd.Series(nifty.index).dt.tz_localize(None)
banknifty.index = pd.Series(banknifty.index).dt.tz_localize(None)
orders_df = pd.DataFrame(kite.orders())
orders_df['order_timestamp'] = pd.Series(orders_df['order_timestamp'].values).dt.floor('Min')
orders_df = orders_df[orders_df['status'] == 'COMPLETE']
orders_df.reset_index(drop=True, inplace=True)
orders_df['ticker value'] = np.zeros(len(orders_df.index))
for xx in range(len(orders_df.index)):
    if orders_df['tradingsymbol'][xx][:5] == 'NIFTY':
        orders_df['ticker value'][xx] = nifty[orders_df['order_timestamp'][xx] == nifty.index].Close
    else:
        orders_df['ticker value'][xx] = dummy_var1[orders_df['order_timestamp'][xx] == nifty.index].Close
pre_df = pd.DataFrame()
entrylist = orders_df[orders_df['transaction_type'] == 'BUY']
exitlist = orders_df[orders_df['transaction_type'] == 'SELL']
entrylist.reset_index(drop=True, inplace=True)
exitlist.reset_index(drop=True, inplace=True)
pre_df['ticker at entry'] = entrylist['ticker value']
pre_df['timestamp at entry'] = entrylist['order_timestamp']
pre_df['entry qnty'] = entrylist['filled_quantity']
pre_df['entry price'] = entrylist['average_price']
pre_df['ticker at exit'] = exitlist['ticker value']
pre_df['timestamp at exit'] = exitlist['order_timestamp']
pre_df['exit qnty'] = exitlist['filled_quantity']
pre_df['exit price'] = exitlist['average_price']
lowest_ticker_in_bw = []
for cc in range(len(pre_df.index)):
    if pre_df['timestamp at exit'].astype(str).values[cc] != 'NaT':
        if (orders_df[orders_df['order_timestamp'] == pre_df['timestamp at exit'].astype(str).values[cc]].tradingsymbol.values[0][:5]) == 'NIFTY':    
            lowest_ticker_in_bw.append(nifty[slice(pre_df['timestamp at entry'].astype(str).values[cc],
                                                   pre_df['timestamp at exit'].astype(str).values[cc])]['Low'].min())
        else:
            lowest_ticker_in_bw.append(dummy_var1[slice(pre_df['timestamp at entry'].astype(str).values[cc],
                                                   pre_df['timestamp at exit'].astype(str).values[cc])]['Low'].min())
    else:
        lowest_ticker_in_bw.append(0)
pre_df['lowest ticker in bw'] = pd.Series(lowest_ticker_in_bw)
highest_ticker_in_bw = []
for cc in range(len(pre_df.index)):
    if pre_df['timestamp at exit'].astype(str).values[cc] != 'NaT':
        if (orders_df[orders_df['order_timestamp'] == pre_df['timestamp at exit'].astype(str).values[cc]].tradingsymbol.values[0][:5]) == 'NIFTY':     
            highest_ticker_in_bw.append(nifty[slice(pre_df['timestamp at entry'].astype(str).values[cc],
                                                    pre_df['timestamp at exit'].astype(str).values[cc])]['High'].max())
        else:
            highest_ticker_in_bw.append(dummy_var1[slice(pre_df['timestamp at entry'].astype(str).values[cc],
                                                    pre_df['timestamp at exit'].astype(str).values[cc])]['High'].max())
    else:
        highest_ticker_in_bw.append(0)
pre_df['highest ticker in bw'] = pd.Series(highest_ticker_in_bw)
pre_df = pre_df[['entry price', 'exit price', 'ticker at entry',
                 'ticker at exit', 'lowest ticker in bw', 'highest ticker in bw',
                 'timestamp at entry', 'timestamp at exit', 'entry qnty', 'exit qnty']]
starting_sheet = pd.read_excel('today_orders.xlsx')
merged = pd.concat([starting_sheet,pre_df], ignore_index=True)
merged.to_excel('today_orders.xlsx', index=False)
