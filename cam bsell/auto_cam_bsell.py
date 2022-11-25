#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kiteconnect import KiteConnect, KiteTicker
from yahoofinancials import YahooFinancials
import datetime as dt
import pandas as pd
import logging
import from_cam_trail

pivot_ticker = '^NSEI'
end = dt.date.today().strftime('%Y-%m-%d')
start = (dt.date.today() - dt.timedelta(10)).strftime('%Y-%m-%d')
yahoo_financials = YahooFinancials(pivot_ticker)
json = yahoo_financials.get_historical_price_data(start, end, 'daily')
ohlv = json[pivot_ticker]['prices']
ohlc_day = pd.DataFrame(ohlv)[['formatted_date', 'open', 'high', 'low', 'close']]
ohlc_day.set_index('formatted_date', inplace=True)
ohlc_day.dropna(inplace=True)

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

kite = KiteConnect(api_key='XXXXXXXXXXXXX')
access_token = open('access_token.txt','r').read()
kite.set_access_token(access_token)
instrument_df = pd.DataFrame(kite.instruments("NFO"))
kws = KiteTicker('XXXXXXXXXXX',kite.access_token)
tokens = [XXXXXXX]

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
            strike_price = ticks - ticks%50 - 50
            today = dt.date.today()
            coming_thursday = today + dt.timedelta(-today.weekday() + 3, weeks=1)
            instrument_type = 'PE'
            try:
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                            exchange=kite.EXCHANGE_NFO,
                                            tradingsymbol=instrument_df[(instrument_df.strike==strike_price) 
                                                                        & (instrument_df.expiry==coming_thursday) 
                                                                        & (instrument_df.instrument_type==instrument_type)].tradingsymbol.values[0],
                                            transaction_type=kite.TRANSACTION_TYPE_BUY,
                                            quantity=50,
                                            product=kite.PRODUCT_NRML,
                                            order_type=kite.ORDER_TYPE_MARKET)
                logging.info(f"Order placed. ID is: {order_id}")
            except Exception as e:
                logging.info(f"Order placement failed: {e.message}")
            kws.close()
            from_cam_trail.connect_and_trailer()
        elif ticks < 1.001*pplevels.l3:
            strike_price = ticks + 100 - ticks%50
            today = dt.date.today()
            coming_thursday = today + dt.timedelta(-today.weekday() + 3, weeks=1)
            instrument_type = 'CE'
            try:
                order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                            exchange=kite.EXCHANGE_NFO,
                                            tradingsymbol=instrument_df[(instrument_df.strike==strike_price) 
                                                                        & (instrument_df.expiry==coming_thursday) 
                                                                        & (instrument_df.instrument_type==instrument_type)].tradingsymbol.values[0],
                                            transaction_type=kite.TRANSACTION_TYPE_BUY,
                                            quantity=50,
                                            product=kite.PRODUCT_NRML,
                                            order_type=kite.ORDER_TYPE_MARKET)
                logging.info(f"Order placed. ID is: {order_id}")
            except Exception as e:
                logging.info(f"Order placement failed: {e.message}")
            kws.close()
            from_cam_trail.connect_and_trailer()
            
    
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.connect()