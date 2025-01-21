import pandas as pd
import yfinance as yf
import praw
from textblob import TextBlob
from datetime import datetime, timedelta
import time
try:
    from config import *
except ImportError:
    print("Please create a config.py file with your Reddit credentials")
    print("See config_template.py for an example")
    exit(1)
    
class DataCollector:
    # initialize data collector with reddit credentials
    def __init__(self, reddit_client_id, reddit_client_secret, reddit_user_agent):
        self.reddit = praw.Reddit(
            client_id = reddit_client_id,
            client_secret = reddit_client_secret,
            user_agent = reddit_user_agent
        )

    # stock price fetching with yfinance
    def get_stock_data(self, ticker, start_date, end_date):
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        # daily returns
        df['Returns'] = df['Close'].pct_change()
        # realized volatility, sqrt(252) * std of daily returns
        df['Realized_Volatility'] = df['Returns'].rolling(window=252).std() * (252**0.5)
        return df
    
    # sentiment score calculation using textblob helper
    def get_sentiment_score(self, text):
        blob = TextBlob(text)
        return blob.sentiment.polarity
    
    # fetch reddit data and analyze sentiment
    
