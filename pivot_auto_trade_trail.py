# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
from kiteconnect import KiteConnect, KiteTicker
from yahoofinancials import YahooFinancials
import datetime as dt
import logging

logging.basicConfig(level=logging.DEBUG)


def tokenLookup(instrument_df, symbol_list):
    return [int(instrument_df[instrument_df.tradingsymbol == symbol]
                .instrument_token.values[0])for symbol in symbol_list]


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
    trailer(ticks[0]['last_price'])


def trailer(ltp):
    if ltp >= entry_stop_list[-1][0]*(1+(trailer_percent/100)):
        entry_stop_list.append(
            (entry_stop_list[-1][0]*(1+(trailer_percent/100)),
             entry_stop_list[-1][1]*(1+(trailer_percent/100))))
    if ltp <= entry_stop_list[-1][1]:
        try:
            order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                        exchange=kite.EXCHANGE_NFO,
                                        tradingsymbol=kite.orders(
                                        )[order_no]['tradingsymbol'],
                                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                                        quantity=kite.orders()[
                                            order_no]['quantity'],
                                        product=kite.PRODUCT_NRML,
                                        order_type=kite.ORDER_TYPE_MARKET)
            logging.info(f"Order placed. ID is: {order_id}")
        except Exception as e:
            logging.info(f"Order placement failed: {e.message}")
        kws.close()


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


def buy():
    try:
        order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NFO,
                                    tradingsymbol=kite.orders(
                                    )[order_no]['tradingsymbol'],
                                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                                    quantity=kite.orders()[
                                        order_no]['quantity'],
                                    product=kite.PRODUCT_NRML,
                                    order_type=kite.ORDER_TYPE_MARKET)
        logging.info(f"Order placed. ID is: {order_id}")
    except Exception as e:
        logging.info(f"Order placement failed: {e.message}")


def sell():
    try:
        order_id = kite.place_order(variety=kite.VARIETY_REGULAR,
                                    exchange=kite.EXCHANGE_NFO,
                                    tradingsymbol=kite.orders(
                                    )[order_no]['tradingsymbol'],
                                    transaction_type=kite.TRANSACTION_TYPE_SELL,
                                    quantity=kite.orders()[
                                        order_no]['quantity'],
                                    product=kite.PRODUCT_NRML,
                                    order_type=kite.ORDER_TYPE_MARKET)
        logging.info(f"Order placed. ID is: {order_id}")
    except Exception as e:
        logging.info(f"Order placement failed: {e.message}")


def trailerwithxx(ltp):
    if ltp > 1.xx*entry_price:
        sell()
        kws.close()


def auto_cam_bsell(pplevels, ticks):
    if ticks > 0.999xx*pplevels.h3:
        sell()
        trailerwith25()
    elif ticks < 1.001xx*pplevels.l3:
        buy()
        trailerwith25()


kite = KiteConnect(api_key='w8rdwxd70igahlor')
request_token = input('enter req token link: ').split('request_token=')[1][:32]
data = kite.generate_session(
    request_token, api_secret='ho7xfopyaqn3d3zt7u36nu5zgkpqhsgg')
kite.set_access_token(data['access_token'])
instrument_df = pd.DataFrame(kite.instruments("NFO"))

kws = KiteTicker('w8rdwxd70igahlor', kite.access_token)
order_no = len(kite.orders()) - 1
entry_price = kite.orders()[order_no]['average_price']
trailer_percent = int(input('enter trailer percent: '))
stoploss = entry_price*(1-(trailer_percent/100))
tickers = [kite.orders()[order_no]['tradingsymbol']]
tokens = tokenLookup(instrument_df, tickers)

entry_stop_list = [(entry_price, stoploss)]
ticker = ['^NSEI']
end = dt.date.today().strftime('%Y-%m-%d')
start = (dt.date.today() - dt.timedelta(10)).strftime('%Y-%m-%d')
close = pd.DataFrame()
for ticker in ticker:
    yahoo_financials = YahooFinancials(ticker)
    json = yahoo_financials.get_historical_price_data(start, end, 'daily')
    ohlv = json[ticker]['prices']
    temp = pd.DataFrame(
        ohlv)[['formatted_date', 'open', 'high', 'low', 'close']]
    temp.set_index('formatted_date', inplace=True)
    temp.dropna(inplace=True)
    close = temp()


kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.connect()
