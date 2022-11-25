#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 23:03:09 2021

@author: aryakumar
"""

def tokenLookup(instrument_df,symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol==symbol]
                .instrument_token.values[0])for symbol in symbol_list]


# package import statement
from smartapi import SmartConnect
from smartapi import SmartWebSocket  #or from smartapi.smartConnect import SmartConnect
#import smartapi.smartExceptions(for smartExceptions)
import pandas as pd
from datetime import datetime
import requests
import numpy as np

url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
d = requests.get(url).json()
token_df = pd.DataFrame.from_dict(d)
token_df['expiry'] = pd.to_datetime(token_df['expiry'])
token_df = token_df.astype({'strike': float})


#create object of call
obj=SmartConnect(api_key="XXXXXK")
                #optional
                #access_token = "your access token",
                #refresh_token = "your refresh_token")

#login api call

data = obj.generateSession("XXXXXX","XXXXXXXX")
refreshToken = data['data']['refreshToken']

#fetch the feedtoken
feedToken=obj.getfeedToken()

url = 'https://kite.zerodha.com/chart/web/tvc/INDICES/XXXXXXX/XXXXXX?theme=dark'
#fetch User Profile
userProfile= obj.getProfile(refreshToken)
#place order
try:
    orderparams = {
        "variety": "NORMAL",
        "tradingsymbol": "XXXXXX",
        "symboltoken": "XXXX",
        "transactiontype": "BUY",
        "exchange": "NSE",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "XXXXXX",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": "1"
        }
    orderId=obj.placeOrder(orderparams)
    print("The order id is: {}".format(orderId))
except Exception as e:
    print("Order placement failed: {}".format(e.message))
#gtt rule creation
# try:
#     gttCreateParams={
#             "tradingsymbol" : "XXXXXX",
#             "symboltoken" : "XXXXX",
#             "exchange" : "NSE", 
#             "producttype" : "MARGIN",
#             "transactiontype" : "BUY",
#             "price" : XXXXXXX,
#             "qty" : 10,
#             "disclosedqty": 10,
#             "triggerprice" : XXXXXXXX,
#             "timeperiod" : 365
#         }
#     rule_id=obj.gttCreateRule(gttCreateParams)
#     print("The GTT rule id is: {}".format(rule_id))
# except Exception as e:
#     print("GTT Rule creation failed: {}".format(e.message))
    
# #gtt rule list
# try:
#     status=["FORALL"] #should be a list
#     page=1
#     count=10
#     lists=obj.gttLists(status,page,count)
# except Exception as e:
#     print("GTT Rule List failed: {}".format(e.message))

#Historic api
# try:
#     historicParam={
#     "exchange": "NSE",
#     "symboltoken": "XXXX5",
#     "interval": "ONE_MINUTE",
#     "fromdate": "2021-02-08 09:00", 
#     "todate": "2021-02-08 09:16"
#     }
#     obj.getCandleData(historicParam)
# except Exception as e:
#     print("Historic Api failed: {}".format(e.message))
# #logout
# try:
#     logout=obj.terminateSession('Your Client Id')
#     print("Logout Successfull")
# except Exception as e:
#     print("Logout failed: {}".format(e.message))


feed_token=XXXXX
FEED_TOKEN=feedToken
CLIENT_CODE='XXXXXX'
# token="mcx_fo|XXXXXX"
token="nse_cm|XXXXX"    #SAMPLE: nse_cm|XXXX5&nse_cm|XXXX&nse_cm|XXXXX&nse_cm|XXXX
# token="mcx_fo|XXXXX&mcx_fo|XXXXXX&mcx_fo|XXXXX&mcx_fo|XXXXX"
task="mw"   # mw|sfi|dp

ss = SmartWebSocket(FEED_TOKEN, CLIENT_CODE)

def on_message(ws, message):
    print("Ticks: {}".format(message))
    
def on_open(ws):
    print("on open")
    ss.subscribe(task,token)
    
def on_error(ws, error):
    print(error)
    
def on_close(ws):
    print("Close")

# Assign the callbacks.
ss._on_open = on_open
ss._on_message = on_message
ss._on_error = on_error
ss._on_close = on_close

ss.connect()
