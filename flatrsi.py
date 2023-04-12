import ccxt
import pandas as pd
import ta
import time
import csv
# read the CSV file of stock symbols
stocks_df = pd.read_csv('indian_stocks.csv')
# set up the exchange
exchange = ccxt.nse2({
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
# create a CSV file and write the header row
with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Symbol', 'Status'])
    while True:
        for symbol in stocks_df['symbol']:
            try:
                # get the last N candles
                timeframe = '15m'
                candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=num_candles)
                # calculate the RSI and WMA(RSI) for each candle
                close_prices = [candle[4] for candle in candles]
                rsis = rsi.rsi(close_prices)
                wma_rsis = wma.wma_indicator(rsis)
                # calculate the average RSI
                avg_rsi = sum(rsis[-num_candles:]) / num_candles
                # check if the RSI and WMA(RSI) are within the threshold percentage of the average
                flag = False
                for i, (rsi, wma_rsi) in enumerate(zip(rsis[-num_candles:], wma_rsis[-num_candles:])):
                    if abs(rsi - avg_rsi) > avg_rsi * (threshold_percent / 100) or abs(wma_rsi - avg_rsi) > avg_rsi * (threshold_percent / 100):
                        print(f'{symbol}: Candle {i+1} RSI is not flat: {rsi}, WMA(RSI) is not flat: {wma_rsi}')
                        writer.writerow([symbol, f'Candle {i+1} RSI is not flat: {rsi}, WMA(RSI) is not flat: {wma_rsi}'])
                        flag = True
                        break
                if not flag:
                    print(f'{symbol}: RSI and WMA(RSI) are flat: {rsis[-num_candles:]}')
                    writer.writerow([symbol, 'Flat'])
            except Exception as e:
                print(f'{symbol}: Error - {e}')
        # wait for 15 minutes before fetching new data
        time.sleep(900)
