import yfinance as yf
import pandas as pd
from nsetools import Nse
# Get the list of all stocks in the NSE 500 index
nse = Nse()
nse_500 = nse.get_index_list()
tickers = [nse.get_stock_codes()[stock] for stock in nse_500]
output_list = []
slope_threshold = 40
rising_days = 10
for ticker in tickers:
    # Get the stock data from Yahoo Finance
    stock_data = yf.Ticker(ticker).history(period="max")
    # Calculate the 44-day and 200-day simple moving averages
    stock_data["SMA44"] = stock_data["Close"].rolling(window=44).mean()
    stock_data["SMA200"] = stock_data["Close"].rolling(window=200).mean()
    # Check if the 44-day SMA has been rising for the past rising_days days, has a slope greater than
    # slope_threshold, and is above the 200-day SMA
    if (all(stock_data["SMA44"].iloc[-rising_days:] > stock_data["SMA44"].iloc[-rising_days-1:-1]) and
        stock_data["SMA44"].iloc[-1] > stock_data["SMA44"].iloc[-2] and
        (stock_data["SMA44"].iloc[-1] - stock_data["SMA44"].iloc[-rising_days]) / rising_days > slope_threshold and
        stock_data["SMA44"].iloc[-1] > stock_data["SMA200"].iloc[-1]):
        output_list.append({"Ticker": ticker})
# Export the output list to a CSV file
pd.DataFrame(output_list).to_csv("output.csv", index=False)