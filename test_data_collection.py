# test_data_collection.py
import matplotlib.pyplot as plt
from data_collection import DataCollector
from datetime import datetime, timedelta
import pandas as pd

def test_data_collection():
    # Import your credentials
    from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
    
    # Initialize collector
    collector = DataCollector(
        REDDIT_CLIENT_ID,
        REDDIT_CLIENT_SECRET,
        REDDIT_USER_AGENT
    )
    
    # Test parameters
    ticker = "AAPL"  # Using Apple as it's frequently discussed
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Test with just 30 days first
    
    print("1. Testing stock data collection...")
    try:
        price_data = collector.get_stock_data(ticker, start_date, end_date)
        print(f"✓ Successfully collected {len(price_data)} days of stock data")
        print("\nFirst few rows of price data:")
        print(price_data.head())
        print("\nColumns in price data:", price_data.columns.tolist())
        
        # Check for missing values
        missing_values = price_data.isnull().sum()
        print("\nMissing values in price data:")
        print(missing_values)
        
        # Basic plotting
        plt.figure(figsize=(12, 6))
        plt.plot(price_data.index, price_data['Close'], label='Close Price')
        plt.title(f'{ticker} Stock Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.savefig('stock_price_test.png')
        plt.close()
        
    except Exception as e:
        print(f"✗ Error collecting stock data: {str(e)}")
        return
    
    print("\n2. Testing Reddit sentiment collection...")
    try:
        sentiment_data = collector.get_reddit_sentiment(ticker, start_date, end_date)
        print(f"✓ Successfully collected {len(sentiment_data)} days of sentiment data")
        print("\nFirst few rows of sentiment data:")
        print(sentiment_data.head())
        
        if len(sentiment_data) > 0:
            # Plot sentiment
            plt.figure(figsize=(12, 6))
            plt.plot(sentiment_data.index, sentiment_data['sentiment'], label='Sentiment')
            plt.title(f'{ticker} Reddit Sentiment')
            plt.xlabel('Date')
            plt.ylabel('Sentiment Score')
            plt.legend()
            plt.savefig('sentiment_test.png')
            plt.close()
            
            # Basic statistics
            print("\nSentiment statistics:")
            print(sentiment_data['sentiment'].describe())
        else:
            print("No sentiment data collected. This might be normal for less discussed stocks.")
            
    except Exception as e:
        print(f"✗ Error collecting sentiment data: {str(e)}")
        return
    
    print("\n3. Testing data alignment...")
    try:
        # Check date ranges
        price_dates = set(price_data.index.date)
        sentiment_dates = set(sentiment_data.index.date)
        common_dates = price_dates.intersection(sentiment_dates)
        
        print(f"Price data date range: {min(price_dates)} to {max(price_dates)}")
        print(f"Sentiment data date range: {min(sentiment_dates)} to {max(sentiment_dates)}")
        print(f"Number of days with both price and sentiment data: {len(common_dates)}")
        
    except Exception as e:
        print(f"✗ Error checking data alignment: {str(e)}")
        return
    
    print("\n✓ All tests completed!")

if __name__ == "__main__":
    test_data_collection()