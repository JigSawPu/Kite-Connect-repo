candlestickdata = data.groupby(data.Date.dt.date).agg({'Price':['min','max','first','last']})
#data is pd, this will create ohlc df
fig = go.Figure(data=[go.Candlestick(x=candlestickdata.index,
open=candlestickdata['Price']['first'],
high=candlestickdata['Price']['max'],
low=candlestickdata['Price']['min'],
close=candlestickdata['Price']['last'])])

fig.update_layout(xaxis_rangeslider_visible=False, xaxis_title='Date', yaxis_title = 'Price (USD $)',
                  title='ticker symbol')

plot(fig, filename='candle.html')