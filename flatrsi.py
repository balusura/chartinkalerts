import ccxt
import pandas as pd
import ta
import time
# read the CSV file of stock symbols
stocks_df = pd.read_csv('indian_stocks.csv')
# set up the exchange
exchange = ccxt.nse({
    'enableRateLimit': True,
})
# set up the RSI indicator with a period of 14
rsi = ta.momentum.RSIIndicator(window=14)
# set up the WMA indicator with a period of 5
wma = ta.trend.WMAIndicator(close=pd.Series(dtype='float64'), window=5)
# prompt the user to enter the number of candles to track
num_candles = int(input('Enter the number of candles to track: '))
# prompt the user to enter the threshold percentage
threshold_percent = float(input('Enter the threshold percentage: '))
while True:
    for symbol in stocks_df['symbol']:
        try:
            # get the last N candles
            timeframe = '15m'
            candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=num_candles)
            # calculate the RSI for each candle
            close_prices = [candle[4] for candle in candles]
            rsi.values = close_prices
            rsis = rsi.rsi()
            # calculate the average RSI
            avg_rsi = sum(rsis[-num_candles:]) / num_candles
            # calculate the weighted moving average of the RSI
            wma.values = rsis
            wma_rsis = wma.wma()
            # check if the RSI and WMA(RSI) are within the threshold percentage of the average
            for i, (rsi, wma_rsi) in enumerate(zip(rsis[-num_candles:], wma_rsis[-num_candles:])):
                if abs(rsi - avg_rsi) > avg_rsi * (threshold_percent / 100) or abs(wma_rsi - avg_rsi) > avg_rsi * (threshold_percent / 100):
                    print(f'{symbol}: Candle {i+1} RSI is not flat: {rsi}, WMA(RSI) is not flat: {wma_rsi}')
                    break
            else:
                print(f'{symbol}: RSI and WMA(RSI) are flat: {rsis[-num_candles:]}')
        except Exception as e:
            print(f'Error fetching data for {symbol}: {e}')
        # wait for the next candle
        time.sleep(exchange.rateLimit / 1000)
    # wait for 15 minutes before fetching data for the next batch of stocks
    time.sleep(15 * 60)