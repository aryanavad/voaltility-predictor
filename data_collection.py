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
    def get_reddit_sentiment(self, ticker, start_date, end_date):
        sentiments = []
        dates = []

        subreddits = ["wallstreetbets", "stocks", "investing"]
        for subreddit in subreddits:
            print(f"Fetching data from r/{subreddit}")

            search_query = f"${ticker} OR {ticker}"
            try:
                submissions = self.reddit.subreddit(subreddit).search(
                    search_query,
                    time_filter = 'year',
                    limit = None
                )

                for submission in submissions:
                    post_date = datetime.fromtimestamp(submission.created_utc)

                    if start_date <= post_date <= end_date:
                        # post content analysis
                        combined_text = f"{submission.title} {submission.selftext}"
                        sentiment = self.get_sentiment_score(combined_text)
                        # top comments analysis
                        submission.comments.replace_more(limit = 0)
                        for comment in submission.comments.list()[:5]:
                            sentiment += self.get_sentiment_score(comment.body)
                        
                        sentiments.append(sentiment)
                        dates.append(post_date)

                    # rate limits for reddit API
                    time.sleep(0.5)
            except Exception as e:
                print(f"Error collecting from r/{subreddit}: {str(e)}")
                continue
        
        # data frame
        sentiment_df = pd.DataFrame({
            'sentiment': sentiments,
            'date': dates
        })

        if len(sentiment_df) > 0:
            sentiment_df.set_index('date', inplace=True)
            daily_sentiment = sentiment_df.resample('D').mean()
            return daily_sentiment.fillna(method='ffill')
        else:
            return pd.DataFrame(columns=['sentiment'])
        
    def main():
        collector = DataCollector (
            REDDIT_CLIENT_ID,
            REDDIT_CLIENT_SECRET,
            REDDIT_USER_AGENT
        )
        # test param
        ticker = "AAPL"
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        print(f"collecting data for {ticker}...")
        # stock data
        price_data = collector.get_stock_data(ticker, start_date, end_date)
        print("stock data collected.")
        # sentiment data
        sentiment_data = collector.get_reddit_sentiment(ticker, start_date, end_date)
        print("reddit sentiment data collected.")

        price_data.to_csv(f"{ticker}_price_data.csv")
        sentiment_data.to_csv(f"{ticker}_sentiment_data.csv")

        print("Data collection complete!")

    if __name__ == "__main__":
        main()


