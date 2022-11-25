#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 13:18:58 2021

@author: aryakumar
"""

from kiteconnect import KiteConnect

kite = KiteConnect(api_key='XXXXXXXXXXXXX')
print(kite.login_url())
request_token = input('enter req token link: ').split('request_token=')[1][:32]
data = kite.generate_session(request_token, api_secret='XXXXXXXXXXXXXXXXXXXXXXXXg')
with open('access_token.txt', 'w') as f:
    f.write(data['access_token'])
